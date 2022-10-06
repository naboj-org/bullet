from django.contrib.auth.views import LoginView as DjLoginView
from django.contrib.auth.views import LogoutView as DjLogoutView
from django.contrib.auth.views import PasswordChangeView as DjPasswordChangeView


class LoginView(DjLoginView):
    template_name = "bullet_admin/login.html"


class LogoutView(DjLogoutView):
    next_page = "/admin/"


class PasswordChangeView(DjPasswordChangeView):
    template_name = "bullet_admin/password_change.html"
    success_url = "/admin/"
