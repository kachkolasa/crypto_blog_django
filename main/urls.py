from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("news/", views.NewsPage.as_view(), name="news"),
    path("reviews/", views.ReviewsPage.as_view(), name="reviews"),
    path("latest/", views.BlogPage.as_view(), name="latest"),
    path("advertise/", views.AdvertisePage.as_view(), name="advertise"),
    path("<slug:slug>/", views.ArticlePage.as_view(), name="post"),
]
 