import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post, Profile


def index(request):
    posts = Post.objects.all().order_by("-post_date")
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    data = paginator.get_page(page)
    context = {"posts": data}
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
    if request.user.id != user_id:
        following = request.user.profile.following.all()
        if "admin" in following:
            print("already followed")
        else:
            request.user.profile.following.add(user_id)
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
        return JsonResponse({"likes": post.likes.count()})