import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Profile


def index(request):
    return render(request, "network/index.html")

def posts(request, page):
    print(page)
    if page == "main":
        posts = Post.objects.all().order_by("-post_date")
        data = [post.serialize() for post in posts] 
        return JsonResponse(data, safe=False)
    elif page == "following":
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            following = list(profile.following.all())
            posts = Post.objects.filter(user__in=following)
            data = [post.serialize() for post in posts] 
            return JsonResponse(data, safe=False)
    elif page == "profile":
        if request.user.is_authenticated:
            profile = Profile.objects.get(user_id=request.user.id)
            posts = Post.objects.filter(user_id=request.user.id)
            data = [post.serialize() for post in posts] 
            return JsonResponse(data, safe=False)
    else:
        return HttpResponseRedirect(reverse("login"))


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

# POSTS
# new post
@login_required
def create(request):

    # Must be request via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request only."}, status=400)

    # Create new post
    body = request.POST.get("body")
    post = Post(user=request.user, body=body)
    post.save()
    return redirect("/")
    # return JsonResponse({"message": "Post created successfully"}, status=201)

# EDIT
@csrf_exempt
@login_required
def edit(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.user:
        if request.method == "PUT":
            edit_body = json.loads(request.body)
            post.body = edit_body["body"]
            post.save()
            return HttpResponse(status=204)
    return HttpResponse(status=403)


@login_required
# ALL FOLLOWING PAGE
def following(request):
    profile = Profile.objects.get(user=request.user)
    following = list(profile.following.all())
    posts = Post.objects.filter(user__in=following)
    context = {"posts": posts}
    return render(request, "network/following.html", context)


# PROFILE
def profile(request, user_id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=user_id)
        posts = Post.objects.filter(user_id=user_id)
        following = list(profile.following.all())
        follower = Profile.objects.filter(following=profile.user)
        context = {"profile": profile, "posts": posts, "following": following, "follower": follower}
        return render(request, "network/profile.html", context)
    else:
        return HttpResponseRedirect(reverse("login"))


# FOLLOW
@login_required
def follow(request, user_id):
    if request.method == "PUT":
        if request.user.id != user_id:
            user = User.objects.get(id=user_id)
            following = request.user.profile.following.all()
            if user in following:
                request.user.profile.following.remove(user_id)
                return JsonResponse({"msg": "Follow"})
            else:
                request.user.profile.following.add(user_id)
                return JsonResponse({"msg": "Unfollow"})
    return redirect("/")


# LIKES
@csrf_exempt
@login_required
def likes(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user.id)
        count = post.likes.count()
        return JsonResponse({"likes": count})