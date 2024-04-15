from django import forms
from django_countries.fields import Country

from competitions.models import Venue


class LiveSetupForm(forms.Form):
    venue_timer = forms.ModelChoiceField(
        label="Venue time",
        help_text="If you use custom start time, select your venue here.",
        queryset=Venue.objects.none(),
        required=False,
    )
    venues = forms.ModelMultipleChoiceField(
        label="Venues",
        queryset=Venue.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
    )
    country = forms.ChoiceField(label="Country results", required=False)
    country_limit = forms.IntegerField(
        label="Country teams limit",
        required=False,
        help_text="How many teams to show in the country results. Leave empty or 0 "
        "to show all.",
    )

    international = forms.BooleanField(label="International results", required=False)
    international_limit = forms.IntegerField(
        label="International teams limit",
        required=False,
        help_text="How many teams to show in the international results. Leave empty "
        "or 0 to show all.",
    )

    hide_contestants = forms.BooleanField(label="Hide contestants", required=False)
    hide_squares = forms.BooleanField(label="Hide squares", required=False)

    def __init__(self, *, competition, **kwargs):
        super().__init__(**kwargs)

        venues = Venue.objects.filter(category__competition=competition)

        self.fields["venue_timer"].queryset = venues.filter(local_start__isnull=False)
        self.fields["venues"].queryset = venues
        self.fields["country"].choices = [("", "-------")] + [
            (c, Country(c).name)
            for c in venues.order_by("country")
            .distinct("country")
            .values_list("country", flat=True)
        ]
