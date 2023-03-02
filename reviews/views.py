from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from news.models import Post, Comment
from django.http import JsonResponse
from django.core.paginator import Paginator
from main.models import UserInfo

class AdminLoginRequired(LoginRequiredMixin):
    login_url = "reviews:login"

    def dispatch(self, request, *args, **kwargs):
        if User.objects.filter(username=request.user.username, is_staff=True).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse("reviews:login"))


class HomeView(AdminLoginRequired, View):
    template_name = "reviews/index.html"
    def get(self, request):
        context = {}
        posts = Post.objects.filter(type="review").order_by("-id")[:10]
        context["posts"] = posts
        return render(request, self.template_name, context)

class CommentsView(AdminLoginRequired, View):
    template_name = "reviews/comments.html"
    def get(self, request):
        context = {}
        if "disable" in request.GET:
            pk = request.GET.get("disable")
            comment = get_object_or_404(Comment, pk=pk, post__type="review")
            comment.is_active = False
            comment.save()
            redirect(reverse("reviews:comments"))
            
        if "active" in request.GET:
            pk = request.GET.get("active")
            comment = get_object_or_404(Comment, pk=pk, post__type="review")
            comment.is_active = True
            comment.save()
            redirect(reverse("reviews:comments"))
            
        posts = Paginator(Comment.objects.filter(post__type="review").order_by("-id"), 30)
        page_number = request.GET.get("page")
        posts_list = posts.get_page(page_number)
        context["comments"] = posts_list
        context["paginator"] = posts
        return render(request, self.template_name, context)

class PostsView(AdminLoginRequired, View):
    template_name = "reviews/posts.html"
    def get(self, request):
        context = {}
        
        posts = Paginator(Post.objects.filter(type="review").order_by("-id"), 30)
        page_number = request.GET.get("page")
        posts_list = posts.get_page(page_number)
        context["posts"] = posts_list
        context["paginator"] = posts
        return render(request, self.template_name, context)

class AuthorsView(AdminLoginRequired, View):
    template_name = "reviews/authors.html"
    def get(self, request):
        context = {}
        
        authors = Paginator(User.objects.all().order_by("-id"), 30)
        page_number = request.GET.get("page")
        authors_list = authors.get_page(page_number)
        context["authors"] = authors_list
        context["paginator"] = authors
        return render(request, self.template_name, context)

class AddAuthorView(AdminLoginRequired, View):
    template_name = "reviews/add-author.html"
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

    def post(self, request):
        first_name  = request.POST["first_name"]
        last_name  = request.POST["last_name"]
        username  = request.POST["username"]
        email  = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if first_name == "" or last_name == "" or email == "" or username == "" or password == "" or password2 == "":
            return JsonResponse({
                "error": "All (*) fields are required"
            })
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "error": "Email already exists."
            })

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "error": "Username already exists."
            })

        if password != password2 :
            return JsonResponse({
                "error" : "Password does not match."
            })
        
        user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=username, is_staff=True)
        info = UserInfo.objects.create(user=user)
        user.set_password(password)
        user.save()

        return JsonResponse({
            "success" : "All changes saved."
        })

class EditAuthorView(AdminLoginRequired, View):
    template_name = "reviews/edit-author.html"
    def get(self, request, username):
        context = {}
        user = get_object_or_404(User, username=username)
        if user.is_superuser:
            return redirect(reverse("reviews:home"))
        context["author"] = user
        return render(request, self.template_name, context)

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        if user.is_superuser:
            return False

        action = request.POST["action"]

        if action == "author":
            first_name  = request.POST["first_name"]
            last_name  = request.POST["last_name"]
            username  = request.POST["username"]
            email  = request.POST["email"]

            if first_name == "" or last_name == "" or email == "" or username == "":
                return JsonResponse({
                    "error": "All (*) fields are required"
                })
            
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                return JsonResponse({
                    "error": "Email already exists."
                })

            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                return JsonResponse({
                    "error": "Username already exists."
                })

            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()

            return JsonResponse({
                "success" : "All changes saved."
            })

        if action == "password":
            password = request.POST["password"]
            password2 = request.POST["password2"]

            if password == "" or password2 == "":
                return JsonResponse({
                    "error": "All (*) fields are required"
                })
            
            if password != password2 :
                return JsonResponse({
                    "error" : "Password does not match."
                })
            
            user.set_password(password)
            user.save()

            return JsonResponse({
                "success" : "All changes saved."
            })

class AddPostView(AdminLoginRequired, View):
    template_name = "reviews/add-post.html"
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        context = {}

        title = request.POST["title"]
        slug = request.POST["slug"]
        content = request.POST["content"]
        status = request.POST["status"]
        
        is_published = 1
        if status == "draft":
            is_published = 0

        if title == "" or slug == "":
            return JsonResponse({
                "error" : "Title & Slug are required."
            })

        if Post.objects.filter(slug=slug).exists():
            return JsonResponse({
                "error" : "Slug already exists"
            })

        post = Post.objects.create(slug=slug, title=title, content=content, type="review", is_published=is_published, author=request.user)
        if "thumbnail" in request.FILES:
            thumbnail = request.FILES["thumbnail"]
            post.thumbnail = thumbnail
            post.save()
        
        redirect = False
        success = "Post was saved as draft."
        if is_published:
            success = "Post was published successfully."
            redirect = True

        return JsonResponse({
            "success" : success,
            "redirect": redirect
        })
   
class EditPostView(AdminLoginRequired, View):
    template_name = "reviews/edit-post.html"
    def get(self, request, slug):
        context = {}
        post = get_object_or_404(Post, slug=slug)
        context["post"] = post
        return render(request, self.template_name, context)
    
    def post(self, request, slug):
        context = {}

        editing_post = get_object_or_404(Post, slug=slug)

        title = request.POST["title"]
        slug = request.POST["slug"]
        content = request.POST["content"]
        status = request.POST["status"]
        
        is_published = 1
        if status == "draft":
            is_published = 0

        if title == "" or slug == "":
            return JsonResponse({
                "error" : "Title & Slug are required."
            })

        if Post.objects.filter(slug=slug).exclude(pk=editing_post.pk).exists():
            return JsonResponse({
                "error" : "Slug already exists"
            })

        editing_post.title = title
        editing_post.slug = slug
        editing_post.content = content
        editing_post.is_published = is_published

        if "thumbnail" in request.FILES:
            thumbnail = request.FILES["thumbnail"]
            editing_post.thumbnail = thumbnail

        editing_post.save()


        success = "Post was saved as draft."
        if is_published:
            success = "Changes were saved successfully."

        return JsonResponse({
            "success" : success
        })

class ProfileView(AdminLoginRequired, View):
    template_name = "reviews/profile.html"
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)
    
    def post(self, request):
        action = request.POST["action"]

        if action == "profile":
            first_name  = request.POST["first_name"]
            last_name  = request.POST["last_name"]
            username  = request.POST["username"]
            email  = request.POST["email"]
            bio  = request.POST["bio"]

            if first_name == "" or last_name == "" or email == "" or username == "":
                return JsonResponse({
                    "error": "All (*) fields are required"
                })
            
            if User.objects.filter(email=email).exclude(username=request.user.username).exists():
                return JsonResponse({
                    "error": "Email already exists."
                })

            if User.objects.filter(username=username).exclude(username=request.user.username).exists():
                return JsonResponse({
                    "error": "Username already exists."
                })

            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.username = username
            request.user.info.bio = bio

            if "profile" in request.FILES:
                request.user.info.profile = request.FILES["profile"]
            
            request.user.save()
            request.user.info.save()

            return JsonResponse({
                "success" : "All changes saved."
            })

        if action == "password":
            password = request.POST["password"]
            password2 = request.POST["password2"]

            if password == "" or password2 == "":
                return JsonResponse({
                    "error" : "All fields are required."
                })

            if password != password2 :
                return JsonResponse({
                    "error" : "Password does not match."
                })
            
            request.user.set_password(password)
            request.user.save()

            return JsonResponse({
                "success" : "Password Changed"
            })

# Create your views here.
class LoginView(View):
    template_name = "reviews/login.html"
    
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name)
        else:
            return redirect("/")

    def post(self, request, *args, **kwargs):
        username = request.POST["username"]
        password = request.POST["password"]
        context = {}
        
        if(username == "" or password == ""):
            context["error"] = "All fields are required"
        else:
            user = User.objects.filter(Q(username=username) | Q(email=username))
            if not user.exists():
                context["error"] = f"No user found with <strong>{username}</strong> as their username or email."
            elif not user[0].is_active:
                context["error"] = f"You have been banned from the website."
            else:
                user_username = user[0].username
                user_auth = authenticate(request, username=user_username, password=password)
                if user_auth is not None:
                    login(request, user_auth)
                    if user[0].is_staff:
                        return redirect(reverse("reviews:home"))
                    else:        
                        context["error"] = "You are not an admin, you are logging in in the wrong place."
                else:
                    context["error"] = f"Incorrect password for <strong>{username}</strong>."
            
        
        return render(request, self.template_name, context)

class LogoutView(View):
    def get(self, request):
        if request.user:
            logout(request)
        

        return redirect("/")