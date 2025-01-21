from competitions.models import Competition
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from documents.models import CertificateTemplate, TexTemplate


class CertificateForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=CertificateTemplate.objects.none(), required=False
    )
    tex_template = forms.ModelChoiceField(
        queryset=TexTemplate.objects.none(),
        required=False,
        label="TeX Template",
    )
    count = forms.IntegerField(
        initial=3,
        help_text="Enter 0 to generate certificates for all teams.",
        min_value=0,
    )
    empty = forms.BooleanField(required=False)

    def __init__(self, competition: Competition, **kwargs):
        super().__init__(**kwargs)
        self.fields["template"].queryset = CertificateTemplate.objects.filter(
            branch=competition.branch
        ).order_by("name")
        self.fields["tex_template"].queryset = TexTemplate.objects.filter(
            competition=competition,
            type=TexTemplate.Type.TEAM_MULTIPLE,
        )

    def clean(self):
        has_template = bool(self.cleaned_data.get("template"))
        has_tex_template = bool(self.cleaned_data.get("tex_template"))

        if not has_template and not has_tex_template:
            raise ValidationError("Please select template or TeX template to continue.")
        if has_template and has_tex_template:
            raise ValidationError(
                "Please don't select template and TeX template at the same time."
            )
        if has_tex_template and self.cleaned_data.get("empty"):
            raise ValidationError(
                "Generating empty certificates with TeX is currently not supported."
            )

        return self.cleaned_data


class TearoffForm(forms.Form):
    first_problem = forms.IntegerField(
        label="First problem",
        initial=1,
        min_value=1,
    )
    backup_teams = forms.IntegerField(
        label="Number of backup teams",
        initial=0,
        min_value=0,
    )
    backup_team_language = forms.ChoiceField(
        label="Backup team language",
    )
    ordering = forms.ChoiceField(
        label="Problem ordering",
        choices=[("align", "Aligned"), ("seq", "Sequential")],
    )
    include_qr_codes = forms.BooleanField(
        label="Include QR code", initial=True, required=False
    )

    def __init__(self, *, problems, first_problem, venue, **kwargs):
        super().__init__(**kwargs)

        self.fields["first_problem"].initial = first_problem
        self.fields["backup_team_language"].choices = list(
            filter(lambda lang: lang[0] in venue.accepted_languages, settings.LANGUAGES)
        )
        self._problem_count = problems
