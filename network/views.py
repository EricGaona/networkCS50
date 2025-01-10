from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.contrib import messages

from .models import User, Post, Follow

from django.views.decorators.csrf import csrf_exempt

import json


def index(request):
    if request.method == "POST":
        content = request.POST["content"]
        if content.strip():
            post = Post(user=request.user, content=content)
            post.save()
            return HttpResponseRedirect(reverse("index"))

    posts = Post.objects.all().order_by("-timestamp").annotate(is_liked=Exists(
        Post.likes.through.objects.filter(
            post_id=OuterRef('pk'),
            user_id=request.user.id
        )
    ))
    posts_json = Post.objects.all().values()
    # posts_likes = posts.annotate(liked=post.likes.filter(id=user.id).exists())

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    list_posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": list_posts,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

#  --------  >>>>>>  Adding the new functions

def all_posts(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    list_posts = paginator.get_page(page_number)

    # print(posts)
    posts_json = Post.objects.all().values()
    posts_serialize = [post.serialize() for post in posts]
    users = User.objects.all()
    users_json = User.objects.all().values()

    return render(request, "network/all_posts.html", {
        "posts": list_posts,
    })


def profile(request, username):
    user = User.objects.get(username=username)
    posts = user.posts.all().order_by("-timestamp")
    is_following = request.user.is_authenticated and user.followers.filter(follower=request.user).exists()
    total_followers = user.followers.count()
    total_following = user.following.count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    list_posts = paginator.get_page(page_number)

    return render(request, "network/profile_page.html", {
        "user_profile": user,
        "posts": list_posts,
        "is_following": is_following,
        "total_followers": total_followers,
        "total_following": total_following,
    })


@login_required
def follow_unfollow(request, username):
    user_to_follow = User.objects.get(username=username)
    is_following = request.user.is_authenticated and user_to_follow.followers.filter(follower=request.user).exists()
    #total_followers = user_to_follow.followers.count()

    if user_to_follow != request.user:
        if not is_following:
            follow = Follow(follower=request.user, followed=user_to_follow)
            follow.save()
        else:
            follow = Follow.objects.filter(follower=request.user, followed=user_to_follow)
            follow.delete()
    return HttpResponseRedirect(reverse("profile_page", args=(username,)))


@login_required
def following(request):
    user = User.objects.get(username=request.user.username)
    following_users = user.following.values_list('followed', flat=True)
    posts = Post.objects.filter(user__id__in=following_users).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    list_posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": list_posts,
    })


@login_required
def like_unlike(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        return JsonResponse({"message": "Unliked successfully.", "like_count": post.like_count()})
    post.likes.add(request.user)
    return JsonResponse({"message": "Liked successfully.", "like_count": post.like_count()})


@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=post_id, user=request.user)  # Ensure user owns the post
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found or you do not have permission to edit this post."}, status=403)

        data = json.loads(request.body)
        new_content = data.get("content", "")

        if new_content.strip() == "":
            return JsonResponse({"error": "Post content cannot be empty."}, status=400)

        post.content = new_content
        post.save()
        return JsonResponse({"message": "Post updated successfully.", "content": post.content}, status=200)
    return JsonResponse({"error": "PUT request required."}, status=400)
