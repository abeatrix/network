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


# FRONT PAGE
# display all posts from all users without login required
def index(request):
    if request.method == "GET":
        # get posts and display newest post first
        posts = Post.objects.all().order_by("-post_date")
        paginator = Paginator(posts, 10)
        page = request.GET.get('page')
        data = paginator.get_page(page)
        context = {"posts": data}
        return render(request, "network/index.html", context)
    return JsonResponse({"error": "GET request only."}, status=400)

# LOGIN
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


# LOGOUT
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# SIGN UP
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


# API FOR CREATING NEW POST
@login_required
def create(request):
    # Must be request via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request only."}, status=400)
    # Create new post
    body = request.POST.get("body")
    post = Post(user=request.user, body=body)
    post.save()
    # redirect to profile page after post is created
    return redirect('profile', user_id=request.user.id)
    # return JsonResponse({"message": "Post created successfully"}, status=201)


# EDIT POST API
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


# ALL FOLLOWING PAGE
# display posts from users they are following
@login_required
def following(request):
    if request.method == "GET":
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            JsonResponse({"error": "Cannot find user."}, status=400)
        following = list(profile.following.all())
        posts = Post.objects.filter(user__in=following).order_by("-post_date")
        context = {"posts": posts}
        return render(request, "network/following.html", context)
    return render(request, "network/login.html")


# PROFILE
def profile(request, user_id):
    # Any user can look at profiles
    if request.method == "GET":
        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            JsonResponse({"error": "Cannot find user."}, status=400)
        # posts are displayed 
        posts = Post.objects.filter(user_id=user_id).order_by("post_date")
        following = list(profile.following.all())
        follower = Profile.objects.filter(following=profile.user)
        context = {"profile": profile, "posts": posts, "following": following, "follower": follower}
        return render(request, "network/profile.html", context)
    return render(request, "network/login.html")



# FOLLOW
@csrf_exempt
@login_required
def follow(request, user_id):
    # check if requester is in the follower list or not
    # if user 
    if request.method == "PUT":
        # users can only follow other user
        if request.user.id != user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                JsonResponse({"error": "Cannot find user."}, status=400)
            following = request.user.profile.following.all()
            if user in following:
                request.user.profile.following.remove(user_id)
                return JsonResponse({"msg": "Follow"})
            else:
                request.user.profile.following.add(user_id)
                return JsonResponse({"msg": "Unfollow"})
        JsonResponse({"error": "Cannot follow yourself."}, status=400)
    # GET method to check follower status
    # then have frontend display accordingly
    elif request.method == "GET":
        user = User.objects.get(id=user_id)
        following = request.user.profile.following.all()
        if user in following:
            return JsonResponse({"msg": "Unfollow"})
        else:
            return JsonResponse({"msg": "Follow"})
    return redirect("/")


# LIKES
@csrf_exempt
@login_required
def likes(request, post_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            JsonResponse({"error": "Cannot find post."}, status=400)
        # If user already liked the post => unlike
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            count = post.likes.count()
            return JsonResponse({"likes": count})
        # like
        else:
            post.likes.add(request.user.id)
            count = post.likes.count()
            return JsonResponse({"likes": count})
    return JsonResponse({"error": "PUT request only"}, status=400)