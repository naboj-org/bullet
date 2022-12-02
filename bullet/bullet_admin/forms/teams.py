from bullet_admin.forms.utils import get_country_choices, get_venue_queryset
from competitions.models import Competition, Venue
from django import forms
from django_countries.fields import CountryField
from users.models import Team, TeamStatus, User


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "school",
            "venue",
            "is_checked_in",
            "consent_photos",
            "is_disqualified",
        ]

    def __init__(self, **kwargs):
        competition: Competition = kwargs.pop("competition")
        super().__init__(**kwargs)

        self.fields["venue"].queryset = Venue.objects.filter(
            category_competition__competition=competition
        ).select_related("category_competition")
        self.fields["school"].required = True


class OperatorTeamForm(TeamForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.pop("school")
        self.fields.pop("venue")
        self.fields.pop("contact_name")
        self.fields.pop("contact_email")
        self.fields.pop("contact_phone")
        self.fields.pop("is_disqualified")


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
        self.fields["countries"].choices = get_country_choices(competition, user)
        self.fields["venues"].queryset = get_venue_queryset(competition, user)

    def apply_filter(self, qs):
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
