from bullet_admin.forms.auth import AuthenticationForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm as DjPasswordResetForm
from django.contrib.auth.views import LoginView as DjLoginView
from django.contrib.auth.views import LogoutView as DjLogoutView
from django.contrib.auth.views import PasswordChangeView as DjPasswordChangeView
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjPasswordResetConfirmView,
)
from django.contrib.auth.views import PasswordResetView as DjPasswordResetView
from django_rq import job

from bullet.utils.email import send_email


class LoginView(DjLoginView):
    template_name = "bullet_admin/login.html"
    form_class = AuthenticationForm

    def form_valid(self, form):
        if form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(6 * 60 * 60)  # 6 hours
        return super().form_valid(form)


class LogoutView(DjLogoutView):
    next_page = "/admin/"


class PasswordChangeView(DjPasswordChangeView):
    template_name = "bullet_admin/password_change.html"
    success_url = "/admin/"


@job
def _send_reset(branch, to_email, context):
    send_email(
        branch,
        to_email,
        "Password reset for your Náboj account",
        "mail/messages/password_reset.html",
        "mail/messages/password_reset.txt",
        context,
    )


class PasswordResetForm(DjPasswordResetForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def __init__(self, branch, **kwargs):
        self.branch = branch
        super().__init__(**kwargs)

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        _send_reset.delay(self.branch, to_email, context)


class PasswordResetView(DjPasswordResetView):
    template_name = "bullet_admin/password_reset.html"
    form_class = PasswordResetForm
    success_url = "/admin/auth/login/"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def form_valid(self, form):
        messages.success(self.request, "Password reset email was sent to your address.")
        return super().form_valid(form)


class PasswordResetConfirmView(DjPasswordResetConfirmView):
    template_name = "bullet_admin/password_reset_confirm.html"
    post_reset_login = True
    success_url = "/admin/"
