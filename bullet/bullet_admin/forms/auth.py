from django import forms
from django.contrib.auth.forms import AuthenticationForm as DjAuthenticationForm


class AuthenticationForm(DjAuthenticationForm):
    remember_me = forms.BooleanField(required=False, label="Remember me")
