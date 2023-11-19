from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings


def upload_path(instance, filename):
    # ファイルの拡張子を取得
    ext = filename.split(".")[-1]
    return "/".join(
        [
            "image",
            str(instance.userpro.id)
            + str(instance.userpro.nickname)
            + str(".")
            + str(ext),
            filename,
        ]
    )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # can login
    is_staff = models.BooleanField(default=False)  # access to admin

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class ProfileModel(models.Model):
    nickname = models.CharField(max_length=255)
    user_pro = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="user_pro", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to=upload_path, blank=True, null=True)

    def __str__(self):
        return self.nickname


class FriendRequest(models.Model):
    ask_from = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="ask_from", on_delete=models.CASCADE
    )
    ask_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="ask_to", on_delete=models.CASCADE
    )
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = (("ask_from", "ask_to"),)

    def __str__(self):
        return str(self.ask_from) + "------>" + str(self.ask_to)


class Message(models.Model):
    message = models.CharField(max_length=140)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sender", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="receiver", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.sender
