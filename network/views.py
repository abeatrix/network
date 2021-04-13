from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Post, Profile, Likes


def index(request):
    posts = Post.objects.all().order_by("-post_date")
    context = {"posts": posts}
    return render(request, "network/index.html", context)


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

# edit
@login_required
def edit(request, post_id):
    if request.user == post.user:
        post = Post.objects.get(id=post_id)
        if request.method == "POST":
            edit_body = request.POST.get("body")
            edited_post = POST(user=request.user, body=body)
            edited_post.save()
            return redirect("/")
        context = {"post": post}
    return redirect("/")



# PROFILE
def profile(request, user_id):
    profile = Profile.objects.get(user_id=user_id)
    posts = Post.objects.filter(user_id=user_id)
    following = list(profile.following.all())
    follower = Profile.objects.filter(following=profile.user)
    if request.method == "POST":
        return True
    else:
        context = {"profile": profile, "posts": posts, "following": following, "follower": follower}
        return render(request, "network/profile.html", context)

# FOLLOW
@login_required
def follow(request, user_id):
    # following_user = Profile.objects.get(user_id=user_id)
    # print(following_user.id)
    # request.user.profile.following.add(following_user.user)
    request.user.profile.following.add(user_id)
    return redirect("/")


# FOLLOWING PAGE
def following(request):
    profile = Profile.objects.get(user=request.user)
    following = list(profile.following.all())
    print(following)
    posts = Post.objects.filter(user__in=following)
    print(posts)
    context = {"posts": posts}
    return render(request, "network/index.html", context)