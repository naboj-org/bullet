from competitions.models import Category, Competition
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form


class ProblemsGenerateForm(Form):
    problem_count = forms.IntegerField(min_value=0, label="Number of problems")

    def __init__(self, competition: "Competition", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.competition = competition
        self.categories = Category.objects.filter(competition=self.competition)
        for category in self.categories:
            self.fields[f"offset_{category.identifier}"] = forms.IntegerField(
                initial=0,
                min_value=0,
                label=f"{category.identifier.title()} offset",
            )

    def clean(self):
        data = super().clean()
        problem_count = data.get("problem_count")
        for category in self.categories:
            if data.get(f"offset_{category.identifier}") > problem_count:
                raise ValidationError(
                    "The offset cannot be greater than the number of problems "
                    "in the competition."
                )

        return data
