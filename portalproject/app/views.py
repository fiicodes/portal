from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect


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

    # Check if the user is already connected
    connection = Connection.objects.filter(user1=user, ended_at=None).first()
    if connection:
        other_user = connection.user2
    else:
        connection = Connection.objects.filter(user2=user, ended_at=None).first()
        if connection:
            other_user = connection.user1
        else:
            # If not connected, find users with the same interests who are online
            interests = user.interests.all()
            online_users = (
                Users.objects.filter(is_online=True, interests__in=interests)
                .exclude(id=user.id)
                .distinct()
            )

            # If no user with the same interests is found, connect with any online user
            if not online_users:
                online_users = Users.objects.filter(is_online=True).exclude(id=user.id)

            # If no online users are found, show an error message
            if not online_users:
                return render(
                    request,
                    "app/base.html",
                    {"error_message": "No online users available for connection."},
                )

            return render(request, "app/match.html", {"other_user": online_users})

    # If connected, display connection details
    context = {
        "first_person": user.full_name,
        "user2": other_user.full_name,
        "gender": other_user.gender,
        "country": other_user.country,
        "connection": connection,
        "user": user,
    }

    return render(request, "app/chatroom.html", context)


def connect_establish(request):

    # Check if the request method is POST
    if request.method == 'POST':
        # Get the user_id from the POST data
        user_id = request.POST.get('user_id')
        # Get the user_id of the current user from the session
        user1 = request.session['user_id']
        # Retrieve the Users objects for both users involved in the connection
        user = Users.objects.get(id=user1)
        other_user = get_object_or_404(Users, id=user_id)

        # Create a new Connection object and save it
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
            "connection_id": connection.id,
        }


        return JsonResponse(context)
    else:

        return JsonResponse({'success': False})


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
    logout(request)
    return render(request, "app/login.html")
