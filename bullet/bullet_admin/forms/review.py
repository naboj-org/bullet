from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from users.models import Team


class ReviewForm(forms.Form):
    number = forms.IntegerField(widget=forms.HiddenInput(), disabled=True)
    is_solved = forms.BooleanField(required=False)
    competition_time = forms.DurationField(required=False)

    def clean(self):
        if self.cleaned_data["is_solved"] and not self.cleaned_data["competition_time"]:
            raise ValidationError("Time must be specified when changing to solved.")

        return self.cleaned_data


def get_review_formset(team: Team):
    problems = (
        team.venue.category.competition.problem_count
        - team.venue.category.first_problem
        + 1
    )
    return formset_factory(ReviewForm, min_num=problems, max_num=problems)
