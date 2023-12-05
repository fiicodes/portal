from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class Interest(models.Model):

    name = models.CharField(max_length=255,null=True, blank=True)
    def __str__(self):

            return self.name

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

class Users(AbstractUser):


    username = None
    email = models.EmailField(_("email address"), unique=True)


    full_name = models.CharField(max_length=100,null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True,null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])



    country = models.CharField(max_length=100,null=True, blank=True)
    password = models.CharField(max_length=255,null=True, blank=True)
    is_online = models.BooleanField(default=False,null=True, blank=True)
    interests = models.ManyToManyField(Interest)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()



    def __str__(self):

            return self.email


class Connection(models.Model):
    user1 = models.ForeignKey(Users, related_name='user1_connections', on_delete=models.CASCADE)
    user2 = models.ForeignKey(Users, related_name='user2_connections', on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True)




class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(Users, on_delete=models.CASCADE)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE)