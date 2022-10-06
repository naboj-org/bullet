from django.contrib.auth.views import LoginView as DjLoginView
from django.contrib.auth.views import LogoutView as DjLogoutView


class LoginView(DjLoginView):
    template_name = "bullet_admin/login.html"


class LogoutView(DjLogoutView):
    next_page = "/admin/"
