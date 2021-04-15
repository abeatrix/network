
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),

    # API Routes
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("create", views.create, name="create"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("likes/<int:post_id>", views.likes, name="likes"),
    path("follow/<int:user_id>", views.follow, name="follow"),
]
