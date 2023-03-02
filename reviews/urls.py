from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"), 
    path("posts/", views.PostsView.as_view(), name="posts"), 
    path("posts/new/", views.AddPostView.as_view(), name="add-post"), 
    path("posts/<slug:slug>/", views.EditPostView.as_view(), name="edit-post"), 
    path("profile/", views.ProfileView.as_view(), name="profile"), 
    path("authors/", views.AuthorsView.as_view(), name="authors"), 
    path("comments/", views.CommentsView.as_view(), name="comments"), 
    path("authors/new/", views.AddAuthorView.as_view(), name="add-author"), 
    path("authors/<str:username>/", views.EditAuthorView.as_view(), name="edit-author"), 
]
     
