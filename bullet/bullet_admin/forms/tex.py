from django import forms
from documents.models import TexTemplate


class LetterCallbackForm(forms.Form):
    file = forms.FileField(required=False)
    tectonic_output = forms.CharField(required=False)
    error = forms.CharField(required=False)


class TexTemplateForm(forms.ModelForm):
    class Meta:
        model = TexTemplate
        fields = ["name", "type", "entrypoint", "template"]

        labels = {
            "name": "Name",
            "type": "Type",
            "entrypoint": "Main .tex file",
            "template": "Sources archive",
        }

        help_texts = {
            "template": "A ZIP archive containing everything needed to build the "
            "document.",
        }
