from bullet_admin.models import BranchRole, CompetitionRole
from competitions.models import Competition, Venue
from countries.models import BranchCountry
from django import forms
from django.core.exceptions import ValidationError
from django_countries.fields import Country
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

    def __init__(
        self, competition: Competition, allowed_object: Venue | Country | None, **kwargs
    ):
        super().__init__(**kwargs)

        venue_qs = Venue.objects.filter(
            category_competition__competition=competition
        ).select_related("category_competition")
        if isinstance(allowed_object, Country):
            venue_qs = venue_qs.filter(country=allowed_object)
        if isinstance(allowed_object, Venue):
            venue_qs = venue_qs.filter(id=allowed_object.id)
        self.fields["venue"].queryset = venue_qs

        countries = set()
        if not allowed_object:
            for c in BranchCountry.objects.filter(branch=competition.branch):
                countries.add(c.country)
        elif isinstance(allowed_object, Country):
            countries.add(allowed_object.code)

        self.fields["country"].choices = list(
            filter(
                lambda x: x[0] in countries or x[0] == "",
                self.fields["country"].choices,
            )
        )

    def clean(self):
        super().clean()
        venue = self.cleaned_data["venue"]
        country = self.cleaned_data["country"]

        if venue and country:
            raise ValidationError(
                "The user cannot be both a venue and a country administrator."
            )
