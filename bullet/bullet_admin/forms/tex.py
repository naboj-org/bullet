import zipfile

from competitions.models import Competition
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from documents.models import TexTemplate


class LetterCallbackForm(forms.Form):
    file = forms.FileField(required=False)
    tectonic_output = forms.CharField(required=False)
    error = forms.CharField(required=False)


class TexTemplateForm(forms.ModelForm):
    class Meta:
        model = TexTemplate
        fields = ["name", "type", "entrypoint", "template"]
        widgets = {
            "template": forms.FileInput(attrs={"accept": "application/zip"}),
        }

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

    def clean_template(self):
        try:
            zipfile.ZipFile(self.cleaned_data["template"])
        except zipfile.BadZipFile:
            raise ValidationError("This file is not a valid ZIP archive.")


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


class TexTeamRenderForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=TexTemplate.objects.none(),
        label="TeX Template",
    )

    def __init__(self, *, competition: Competition, **kwargs):
        super().__init__(**kwargs)
        self.fields["template"].queryset = TexTemplate.objects.filter(
            competition=competition,
        ).filter(
            Q(type=TexTemplate.Type.TEAM_MULTIPLE)
            | Q(type=TexTemplate.Type.TEAM_SINGLE)
        )
