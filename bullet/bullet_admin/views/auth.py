from django.contrib.auth.views import LoginView as DjLoginView


class LoginView(DjLoginView):
    template_name = "bullet_admin/login.html"
