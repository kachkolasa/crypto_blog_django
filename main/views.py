from django.shortcuts import render, get_object_or_404
from django.views import View
from news.models import Post, Comment
from .models import UserInfo
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.
class HomePage(View):
    template_name = "main/index.html"
    def get(self, request, *args, **kwargs):
        context = {}
        posts = Post.objects.filter(is_published=True).order_by("-id")[:6]
        news = Post.objects.filter(is_published=True).filter(type="news").order_by("-id")[:6]
        reviews = Post.objects.filter(is_published=True).filter(type="review").order_by("-id")[:6]

        context["posts"] = posts
        context["news"] = news
        context["reviews"] = reviews
        context["nbar"] = "home"

        return render(request, self.template_name, context)

class NewsPage(View):
    template_name = "main/category.html"
    def get(self, request, *args, **kwargs):
        context = {}
        
        posts = Paginator(Post.objects.filter(type="news").filter(is_published=True).order_by("-id"), 15)
        page_number = request.GET.get("page")
        posts_list = posts.get_page(page_number)
        context["posts"] = posts_list
        context["paginator"] = posts
        context["category"] = "News"
        context["nbar"] = "news"
        

        return render(request, self.template_name, context)

class ReviewsPage(View):
    template_name = "main/category.html"
    def get(self, request, *args, **kwargs):
        context = {}
        
        posts = Paginator(Post.objects.filter(type="review").filter(is_published=True).order_by("-id"), 15)
        page_number = request.GET.get("page")
        posts_list = posts.get_page(page_number)
        context["posts"] = posts_list
        context["paginator"] = posts
        context["category"] = "Reviews"
        context["nbar"] = "review"
        

        return render(request, self.template_name, context)

class BlogPage(View):
    template_name = "main/category.html"
    def get(self, request, *args, **kwargs):
        context = {}
        
        posts = Paginator(Post.objects.filter(is_published=True).order_by("-id"), 15)
        page_number = request.GET.get("page")
        posts_list = posts.get_page(page_number)
        context["posts"] = posts_list
        context["paginator"] = posts
        context["category"] = "What's New"
        context["nbar"] = "home"
        

        return render(request, self.template_name, context)

class AdvertisePage(View):
    template_name = "main/advertise.html"
    def get(self, request, *args, **kwargs):
        context = {}
        
        context["category"] = "Advertise"
        context["nbar"] = "advertise"
        

        return render(request, self.template_name, context)

class ArticlePage(View):
    template_name = "main/article.html"
    def get(self, request, slug, *args, **kwargs):
        context = {}

        post = get_object_or_404(Post, is_published=True, slug=slug)
        context["post"] = post

        comments = Comment.objects.filter(post__slug=slug, is_active=True)
        context["comments"] = comments

        author_posts = Post.objects.filter(author=post.author, is_published=True).exclude(slug=slug).order_by("-id")[:10]
        context["author_posts"] = author_posts

        similar_posts = Post.objects.filter(type=post.type, is_published=True).exclude(slug=slug)[:10]
        context["similar_posts"] = similar_posts

        
        context["nbar"] = post.type

        return render(request, self.template_name, context)
    
    def post(self, request, slug):
        post = get_object_or_404(Post, is_published=True, slug=slug)

        if "comment" in request.POST:
            name = request.POST["name"]
            comment = request.POST["comment"]

            if name == "" or comment == "":
                return JsonResponse({
                    "error" : "All fields are required."
                })
                
            Comment.objects.create(name=name, text=comment, is_active=True, post=post)

            return JsonResponse({
                "success": "Comment added successfully."
            })