from django import forms
from django.core.exceptions import ValidationError
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


class TexRenderForm(forms.Form):
    context = forms.JSONField(
        initial=dict,
        required=False,
        label="Data",
        help_text="JSON-formatted data that will be available to the template.",
    )

    def clean_context(self):
        context = self.cleaned_data["context"]
        if not isinstance(context, dict):
            raise ValidationError("This must be a JSON object.")

        return context
