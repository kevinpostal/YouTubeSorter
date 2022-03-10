from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import Credentials

User = get_user_model()


class CredentialsAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    list_display = ["email", "client_id", "is_superuser", "created_at", "updated_at"]
    list_filter = ["is_superuser"]
    ordering = ["pk"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("email", "password", "created_at", "updated_at")}),
        (
            "Credential info",
            {
                "fields": (
                    "token",
                    "refresh_token",
                    "token_uri",
                    "client_id",
                    "client_secret",
                    "scopes",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_superuser")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "is_staff", "is_superuser"),
            },
        ),
    )


admin.site.register(Credentials, CredentialsAdmin)
admin.site.unregister(Group)
