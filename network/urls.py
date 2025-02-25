from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("all-posts", views.all_posts, name="all_posts"),
    path("profile/<str:username>", views.profile, name="profile_page"),
    path("following", views.following, name="following"),
    path("like/<int:post_id>", views.like_unlike, name="like_unlike"),
    path("follow/<str:username>", views.follow_unfollow, name="follow_unfollow"),
    path("edit-post/<int:post_id>", views.edit_post, name="edit_post"),
]
