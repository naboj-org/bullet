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


class SequenceListField(forms.CharField):
    def __init__(self, *args, min_value=None, max_value=None, **kwargs):
        self.min_value = 0 if min_value is None else min_value
        self.max_value = 999 if max_value is None else max_value
        super().__init__(*args, **kwargs)

    def clean(self, value):
        vals = super().clean(value).strip(",").strip()
        result_set = set()
        if len(vals) == 0:
            return set()

        for val in vals.split(","):
            numbers = []
            parts = val.split("-")
            if len(parts) > 2:
                raise ValidationError("Invalid sequence: " + f"'{val}'")

            try:
                for x in parts:
                    num = int(x)
                    if num > self.max_value:
                        raise ValidationError("Number too large: " + x)
                    if num < self.min_value:
                        raise ValueError
                    numbers.append(num)
            except ValueError:
                raise ValidationError("Invalid input: " + f"'{val}'")

            if len(numbers) == 1:
                result_set.add(numbers[0])
            elif len(numbers) == 2:
                if numbers[0] > numbers[1]:
                    raise ValidationError("Invalid sequence: " + f"'{val}'")
                result_set.update(range(numbers[0], numbers[1] + 1))

        return result_set


class TearoffForm(forms.Form):
    primary_tearoff_language = forms.ChoiceField(
        label="Primary language of the Venue",
        required=True,
    )

    teams_selected = SequenceListField(
        label="Selected teams",
        help_text='Teams to be included in the printed tearoffs. Syntax example: "1-4, 5, 7" (teams with numbers 1 to 4, 5 and 7). Leave empty to include all available teams',
        required=False,
        max_length=500,
    )

    first_problem = forms.IntegerField(
        label="First problem",
        initial=1,
        min_value=1,
    )
    backup_teams = forms.IntegerField(
        label="Number of Backup teams",
        initial=0,
        min_value=0,
    )
    backup_team_language = forms.ChoiceField(
        label="Backup team language",
    )

    language_print_options = forms.ChoiceField(
        label="Language print options",
        choices=[("mixed", "Mixed"), ("mono", "Monolingual"), ("bil", "Bilingual")],
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
        accepted_languages = list(
            filter(lambda lang: lang[0] in venue.accepted_languages, settings.LANGUAGES)
        )
        self.fields["primary_tearoff_language"].choices = [
            ("", "---------")
        ] + accepted_languages
        self.fields["backup_team_language"].choices = accepted_languages
        self._problem_count = problems
