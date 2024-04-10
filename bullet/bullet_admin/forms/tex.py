from django import forms


class LetterCallbackForm(forms.Form):
    file = forms.FileField(required=False)
    tectonic_output = forms.CharField(required=False)
    error = forms.CharField(required=False)
