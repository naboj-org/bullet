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
        fields = ("venue_objects", "countries", "can_delegate")
        widgets = {
            "countries": forms.CheckboxSelectMultiple(),
            "venue_objects": forms.CheckboxSelectMultiple(),
        }

    def __init__(
        self,
        competition: Competition,
        allowed_objects: list[Venue] | list[Country] | None,
        **kwargs
    ):
        super().__init__(**kwargs)

        venue_qs = (
            Venue.objects.filter(category_competition__competition=competition)
            .select_related("category_competition")
            .order_by("name", "category_competition__identifier")
        )
        if len(allowed_objects):
            if isinstance(allowed_objects[0], Country):
                venue_qs = venue_qs.filter(country__in=allowed_objects)
            if isinstance(allowed_objects[0], Venue):
                venue_qs = venue_qs.filter(id__in=[x.id for x in allowed_objects])
        self.fields["venue_objects"].queryset = venue_qs

        countries = set()
        if not allowed_objects:
            for c in BranchCountry.objects.filter(branch=competition.branch):
                countries.add(c.country)
        elif len(allowed_objects) and isinstance(allowed_objects[0], Country):
            for country in allowed_objects:
                countries.add(country.code)

        self.fields["countries"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] in countries or x[0] == "",
                    self.fields["countries"].choices,
                )
            )
        )

    def clean(self):
        super().clean()
        venues = self.cleaned_data["venue_objects"]
        countries = self.cleaned_data["countries"]

        if venues and countries:
            raise ValidationError(
                "The user cannot be both a venue and a country administrator."
            )
