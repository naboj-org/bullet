from competitions.models import Competition
from django import forms
from django.core.validators import FileExtensionValidator
from problems.models import Problem


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = [
            "number",
            "web_start",
            "registration_start",
            "registration_second_round_start",
            "registration_end",
            "competition_start",
            "competition_duration",
            "results_freeze",
            "problem_count",
            "is_cancelled",
        ]

        help_texts = {
            "web_start": "Date from when the competition will be shown on homepage",
            "results_freeze": "How long before the competition "
            "end the result table freezes",
        }

        labels = {"is_cancelled": "Cancel the competition?", "number": "Year"}

        widgets = {
            "web_start": forms.DateTimeInput(attrs={"type": "datetime"}),
            "registration_start": forms.DateTimeInput(attrs={"type": "datetime"}),
            "registration_second_round_start": forms.DateTimeInput(
                attrs={"type": "datetime"}
            ),
            "registration_end": forms.DateTimeInput(attrs={"type": "datetime"}),
            "competition_start": forms.DateTimeInput(attrs={"type": "datetime"}),
        }

    def save(self, commit: bool = True):
        obj = super().save(commit=True)

        current_problems = Problem.objects.filter(competition=obj)
        current_count = current_problems.count()
        requested_count = self.cleaned_data["problem_count"]
        if current_count != requested_count:
            if current_count > requested_count:
                current_problems.filter(number__gt=requested_count).delete()
            else:
                for i in range(current_count + 1, requested_count + 1):
                    Problem.objects.create(competition=obj, number=i)

        return obj


class TearoffUploadForm(forms.Form):
    problems = forms.FileField(
        label="Tearoff file",
        help_text="A ZIP file containing one PDF for every language, "
        "or a single PDF file. The file names should be the 2-letter language code.",
        validators=[
            FileExtensionValidator(["pdf", "zip"]),
        ],
    )
