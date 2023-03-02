from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify 
from django.urls import reverse

# Create your models here.
class Post(models.Model):
    type = models.CharField(max_length=25, default="news")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to="%Y/%m/%d", default="post-default.jpg")
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    
    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }
        return reverse('main:post', kwargs=kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    is_active = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_reply = models.BooleanField(default=False)
    text = models.TextField()
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name