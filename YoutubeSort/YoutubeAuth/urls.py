from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback')
]