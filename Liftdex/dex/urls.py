from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import EmailAuthenticationForm


urlpatterns = [
    path("", views.home, name="home"),
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/<slug:slug>/", views.exercise_detail, name="exercise_detail"),
    path("exercise/<slug:slug>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    # auth
    path("accounts/signup/", views.signup, name="signup"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form = EmailAuthenticationForm, 
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("accounts/me/", views.account_detail, name="account_detail"),
]