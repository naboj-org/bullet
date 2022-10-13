from bullet_admin.models import BranchRole, CompetitionRole
from competitions.models import Competition, Venue
from countries.models import BranchCountry
from django import forms
from users.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class BranchRoleForm(forms.ModelForm):
    class Meta:
        model = BranchRole
        fields = ("is_translator", "is_admin")


class CompetitionRoleForm(forms.ModelForm):
    class Meta:
        model = CompetitionRole
        fields = ("venue", "country", "can_delegate")

    def __init__(self, competition: Competition, **kwargs):
        super().__init__(**kwargs)
        self.fields["venue"].queryset = Venue.objects.filter(
            category_competition__competition=competition
        ).select_related("category_competition")
        countries = set()
        for c in BranchCountry.objects.filter(branch=competition.branch):
            countries.add(c.country)

        self.fields["country"].choices = list(
            filter(
                lambda x: x[0] in countries or x[0] == "",
                self.fields["country"].choices,
            )
        )
