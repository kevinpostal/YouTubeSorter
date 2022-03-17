from typing import TypeVar

from celery import current_app
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.base import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

_model = TypeVar("_model", bound=Model)


class CustomUserManager(BaseUserManager):
    """Custom User Manager inherited from `BaseUserManager`.

    Reference:
            https://docs.djangoproject.com/en/dev/topics/db/managers/
    """

    def create_user(self, email: str, password: str | None, **extra_fields) -> _model:
        """Create and save a user.

        Args:
            email (str): email of user.
            password (str, optional): password of user. Defaults to None.
            extra_fields: Arbitrary keyword arguments.

        Returns:
            Credentials

        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str | None) -> _model:
        """Create and save a user with super.

        Args:
            email (str): email of user
            password (str, optional): password of user. Defaults to None.

        Returns:
            Credentials

        """
        user = self.create_user(
            email,
            password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Credentials(AbstractUser):
    username = None
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_uri = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.JSONField(default=str)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    @property
    def has_credentials(self):
        """Check if user has credentials saved.

        Returns:
            bool: True of False

        """
        return all(self.credentials_to_dict().values())

    def import_youtube_liked_videos(self):
        """Import all youtube videos user has liked."""
        current_app.send_task("YoutubeSort.tasks.import_youtube_liked_videos_task", (self.id,))

    def credentials_to_dict(self) -> dict:
        """Convert Credentials object to a dictonary for oauth.

        Returns:
            dict: credentials dictonary for google oauth.

        """
        return {
            "token": self.token,
            "refresh_token": self.refresh_token,
            "token_uri": self.token_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": self.scopes,
        }


@receiver(post_save, sender=Credentials, dispatch_uid="import_youtube_signal")
def import_youtube(sender: Credentials, instance, created, **kwargs):
    """Signal on `YoutubeVideo` post_save for scraping youtube liked videos.

    Args:
        sender (Credentials): Credentials Model.
        instance (_type_): Credentials Instance that was saved.
        created (_type_): If it was created rather than updated.
        kwargs: https://docs.djangoproject.com/en/3.2/ref/signals/#post-save

    """
    if created and instance.has_credentials:
        current_app.send_task("YoutubeSort.tasks.import_youtube_liked_videos_task", (instance.id,))
