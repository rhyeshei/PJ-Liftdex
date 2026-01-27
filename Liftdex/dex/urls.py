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

    path("accounts/me/edit/", views.account_edit, name="account_edit"),
    
    path(
        "accounts/password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html"
        ),
        name="password_change"
    ),
    
    path(
        "accounts/password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done"
    ),

    path(
        "accounts/password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt"
        ),
        name="password_reset"
    ),
    
    path(
        "accounts/password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done"
    ),
    
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm"
    ),
    
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),

]