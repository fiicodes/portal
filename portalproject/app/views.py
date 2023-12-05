from django.shortcuts import render
import datetime
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from datetime import datetime
from .models import Users, Interest, Connection
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            # Manually set the hashed password

            user.is_online = True
            user.save()
            form.save_m2m()
            request.session["user_id"] = user.id

            return redirect(
                "loginfunc"
            )  # Redirect to  login page after successful registration
    else:
        form = SignUpForm()

    return render(request, "app/signup.html", {"form": form})


def loginfunc(request):
    User = get_user_model()

    if request.method == "POST":
        input_field = request.POST.get("email_or_phone")
        password = request.POST.get("password")

        user = None
        # Check the input is email or phone number
        if "@" in input_field:
            # find User  by email in model
            user = User.objects.filter(email=input_field).first()

        else:
            # find User  by phone in model
            user = User.objects.filter(phone=input_field).first()
        # print(user)
        # print(check_password(password,user.password))
        # print(user.password)

        if user and check_password(password, user.password):
            user.is_online = True

            request.session["user_id"] = user.id

            user.save()
            # print('loggedin')
            return redirect("toggle_online")
        else:
            # If user is not found or password is incorrect, show an error message
            error_message = "Invalid email/phone number or password"
            return render(request, "app/login.html", {"error_message": error_message})
    else:
        return render(request, "app/login.html")


def toggle_online(request):
    user_id = request.session["user_id"]

    user = Users.objects.get(id=user_id)
    user.is_online = not user.is_online
    user.save()

    return render(request, "app/goonline.html", {"user": user})


def connect_users(request):
    user_id = request.session["user_id"]
    user = Users.objects.get(id=user_id)

    if Connection.objects.filter(user1=user, ended_at=None).exists():
        connection = Connection.objects.get(user1=user, ended_at=None)
        return render(
            request,
            "app/chatroom.html",
            {
                "first_person": user.full_name,
                "user2": connection.user2.full_name,
                "gender": connection.user2.gender,
                "country": connection.user2.country,
                "connection": connection,
                "user": user,
            },
        )
    if Connection.objects.filter(user2=user, ended_at=None).exists():
        connection = Connection.objects.get(user2=user, ended_at=None)
        return render(
            request,
            "app/chatroom.html",
            {
                "first_person": user.full_name,
                "user2": connection.user1.full_name,
                "gender": connection.user1.gender,
                "country": connection.user1.country,
                "connection": connection,
                "user": user,
            },
        )
    interests = user.interests.all()
    usr_idd = user.id

    # First, try to find another user with the same interests who is online
    user2 = (
        Users.objects.filter(is_online=True, interests__in=interests)
        .exclude(id=usr_idd)
        .distinct()
    )

    context = {
        "other_user": user2,
    }

    # If no user is found, connect with anyone who is online
    if not user2:
        online_user = Users.objects.filter(is_online=True).exclude(id=user.id)

        return render(request, "app/match.html", {"online_user": online_user})
    # If no online user is found, show an error message
    if not user2:
        return render(request, "app/noonline.html")
    return render(request, "app/match.html", context)


def connect_establish(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user1 = request.session["user_id"]
        user = Users.objects.get(id=user1)
        other_user = get_object_or_404(Users, id=user_id)
        connection = Connection.objects.create(user1=user, user2=other_user)
        connection.save()

        context = {
            "user1": {
                "id": user.id,
                "full_name": user.full_name,
            },
            "user2": {
                "id": other_user.id,
                "full_name": other_user.full_name,
            },
            "connection": {
                "id": connection.id,
                "ended_at": connection.ended_at.isoformat()
                if connection.ended_at
                else None,
            },
        }

        return JsonResponse(context)
    else:
        return JsonResponse({"success": False})


def connected(request):
    person1 = request.session["user_id"]
    first_person = Users.objects.get(id=person1)
    connection_id = request.GET.get("connection")
    connection = get_object_or_404(Connection, id=connection_id)
    return render(
        request,
        "app/chatroom.html",
        {
            "first_person": first_person,
            "user2": connection.user2.full_name,
            "gender": connection.user2.gender,
            "country": connection.user2.country,
            "connection": connection,
            "user": first_person,
        },
    )


def user_logout(request):
    user_id = request.session["user_id"]
    user = Users.objects.get(id=user_id)

    connection = request.GET.get("connection")
    try:
        connection = Connection.objects.get(id=connection)
        connection.ended_at = datetime.now()
        connection.save()
        user.is_online = False
        user.save()

        return render(request, "app/login.html")
    except Connection.DoesNotExist:
        raise Exception("No Connection id")
