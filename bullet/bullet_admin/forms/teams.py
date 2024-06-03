from competitions.models import Category, Competition, Venue, Wildcard
from django import forms
from django.db import models
from django_countries.fields import CountryField
from users.models import SpanishTeamData, Team, TeamStatus, User

from bullet_admin.fields import SchoolInput
from bullet_admin.forms.utils import (
    get_country_choices,
    get_language_choices,
    get_language_choices_for_venue,
)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "language",
            "school",
            "venue",
            "is_checked_in",
            "consent_photos",
            "is_disqualified",
            "number",
        ]

        help_texts = {
            "consent_photos": "It is important that you have at least a verbal consent "
            "to take photos of this team. Consult your local laws for more "
            "information.",
        }

    def __init__(self, **kwargs):
        competition: Competition = kwargs.pop("competition")
        super().__init__(**kwargs)

        self.fields["venue"].queryset = Venue.objects.for_competition(competition)
        if kwargs["instance"]:
            self.fields["language"].choices = get_language_choices_for_venue(
                self.instance.venue
            )
        else:
            self.fields["language"].choices = get_language_choices(competition.branch)

        self.fields["school"].required = True


class OperatorTeamForm(TeamForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.pop("school")
        self.fields.pop("venue")
        self.fields.pop("contact_name")
        self.fields.pop("contact_email")
        self.fields.pop("contact_phone")
        self.fields.pop("number")
        self.fields.pop("is_disqualified")


class SpanishTeamForm(TeamForm):
    spanish_is_verified = forms.BooleanField(label="Is verified?")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance:
            team: Team = self.instance
            if hasattr(team, "spanish_data"):
                self.fields[
                    "spanish_is_verified"
                ].initial = team.spanish_data.is_verified

    def save(self, commit=True):
        self.instance = super().save(commit)

        if self.instance.id:
            if hasattr(self.instance, "spanish_data"):
                sd: SpanishTeamData = self.instance.spanish_data
            else:
                sd = SpanishTeamData(team=self.instance)
            sd.is_verified = self.cleaned_data.get("spanish_is_verified")
            sd.save()

        return self.instance


class TeamFilterForm(forms.Form):
    countries = CountryField(multiple=True, blank=True).formfield(
        widget=forms.CheckboxSelectMultiple
    )
    venues = forms.ModelMultipleChoiceField(
        Venue.objects.none(), required=False, widget=forms.CheckboxSelectMultiple
    )
    statuses = forms.MultipleChoiceField(
        choices=TeamStatus.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, competition: Competition, user: User, **kwargs):
        super().__init__(**kwargs)
        self._competition = competition
        self._user = user
        self.fields["countries"].choices = get_country_choices(competition, user)
        self.fields["venues"].queryset = Venue.objects.for_user(competition, user)

    def apply_filter(self, qs):
        crole = self._user.get_competition_role(self._competition)
        if crole.countries:
            qs = qs.filter(venue__country__in=crole.countries)
        elif crole.venues:
            qs = qs.filter(venue__in=crole.venues)

        if not self.is_valid():
            return qs

        if self.cleaned_data["countries"]:
            qs = qs.filter(venue__country__in=self.cleaned_data["countries"])
        if self.cleaned_data["venues"]:
            qs = qs.filter(venue__in=self.cleaned_data["venues"])
        if self.cleaned_data["statuses"]:
            statuses = self.cleaned_data["statuses"]
            qs = qs.has_status(statuses)
        return qs


class TeamExportForm(TeamFilterForm):
    class Format(models.TextChoices):
        JSON = "json", "JSON"
        CSV = "csv", "CSV"
        YAML = "yaml", "YAML"

    format = forms.ChoiceField(label="Export format", choices=Format.choices)


class WildcardForm(forms.ModelForm):
    class Meta:
        model = Wildcard
        fields = ["school", "category", "note"]

        widgets = {
            "school": SchoolInput(),
        }

    def __init__(self, **kwargs):
        self.competition = kwargs.pop("competition")
        super().__init__(**kwargs)

        self.fields["category"].queryset = Category.objects.filter(
            competition=self.competition
        )

    def save(self, commit=True):
        wildcard = super().save(commit=False)
        wildcard.competition = self.competition
        if commit:
            wildcard.save()

        return wildcard
