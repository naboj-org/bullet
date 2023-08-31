from competitions.models import Category, Competition
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form
from problems.models import CategoryProblem, Problem


class CategoryProblemForm(Form):
    problem_count = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        self.BRANCH = kwargs.pop("branch", None)
        super().__init__(*args, **kwargs)
        self.competition = Competition.objects.get_current_competition(self.BRANCH)
        self.fields["problem_count"].initial = Problem.objects.filter(
            competition=self.competition
        ).count()
        self.fields["problem_count"].disabled = Problem.objects.filter(
            competition=self.competition
        ).exists()
        self.categories = Category.objects.filter(competition=self.competition)
        has_problems = Problem.objects.filter(competition=self.competition).count() > 0
        for category in self.categories:
            categoryOffset = (
                CategoryProblem.objects.filter(category=category)
                .order_by("number")
                .first()
            )
            initial = 0
            if categoryOffset is not None:
                initial = categoryOffset.number - 1
            self.fields[
                "offset_{id}".format(id=category.identifier)
            ] = forms.IntegerField(initial=initial, min_value=0, disabled=has_problems)

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
