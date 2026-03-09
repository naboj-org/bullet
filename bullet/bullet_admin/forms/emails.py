from competitions.models import Competition, Venue
from django import forms
from users.models import EmailCampaign, User
from web.widgets import MarkdownWidget

from bullet_admin.access import is_branch_admin
from bullet_admin.forms.utils import get_country_choices, get_language_choices


class EmailCampaignForm(forms.ModelForm):
    class Meta:
        model = EmailCampaign

        fields = (
            "subject",
            "template",
            "team_countries",
            "team_languages",
            "team_venues",
            "team_statuses",
            "team_contestants",
        )

        widgets = {
            "team_countries": forms.CheckboxSelectMultiple(),
            "team_languages": forms.CheckboxSelectMultiple(),
            "team_venues": forms.CheckboxSelectMultiple(),
            "team_statuses": forms.CheckboxSelectMultiple(),
            "template": MarkdownWidget(attrs={"rows": 30}),
        }

        help_texts = {
            "team_contestants": "Comma separated list of numbers.",
        }

    def __init__(self, competition: Competition, user: User, **kwargs):
        super().__init__(**kwargs)
        self.competition = competition
        self.user = user

        self.fields["team_countries"].choices = get_country_choices(competition, user)
        self.fields["team_languages"].choices = get_language_choices(competition.branch)
        self.fields["team_venues"].queryset = Venue.objects.for_user(competition, user)

    def clean(self):
        cleaned_data = super().clean()

        # Branch admins can create any campaign
        if is_branch_admin(self.user, self.competition):
            return cleaned_data

        team_countries = cleaned_data.get("team_countries", [])
        team_venues = cleaned_data.get("team_venues", [])

        # Only branch admin can create global emails (no country/venue filters)
        if not team_countries and not team_venues:
            raise forms.ValidationError(
                "Only branch administrators can create global email campaigns. "
                "Please select at least one country or venue."
            )

        return cleaned_data
