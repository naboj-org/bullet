from competitions.models import Category, Competition
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form
from problems.models import Problem


class CategoryProblemForm(Form):
    problem_count = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        self.BRANCH = kwargs.pop("branch", None)
        self.problem_count = kwargs.pop("problem_count", None)
        self.offsets = kwargs.pop("offsets", None)
        super().__init__(*args, **kwargs)
        self.fields["problem_count"].initial = self.problem_count
        self.competition = Competition.objects.get_current_competition(self.BRANCH)
        self.categories = Category.objects.filter(competition=self.competition)
        for category in self.categories:
            self.fields[
                "offset_{id}".format(id=category.identifier)
            ] = forms.IntegerField(initial=0, min_value=0)

    def clean(self):
        data = super().clean()
        problem_count = data.get("problem_count")
        for category in self.categories:
            if data.get("offset_{id}".format(id=category.identifier)) > problem_count:
                raise ValidationError(
                    "Offset cannot be greater than number of problems in competition"
                )

        if Problem.objects.filter(competition=self.competition).count() > 0:
            raise ValidationError("Problems already exist, cannot change anything here")
