from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="info")
    profile = models.ImageField(upload_to="%Y/%m/%d", default="profile.svg")
    bio = models.TextField()

    def __str__(self):
        return self.user.username