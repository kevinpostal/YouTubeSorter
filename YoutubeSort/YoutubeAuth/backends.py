from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse


class EmailorUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            login(request, user)
            return user
        return None
