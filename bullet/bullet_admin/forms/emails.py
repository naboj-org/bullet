from bullet_admin.forms.utils import get_country_choices, get_language_choices
from competitions.models import Competition, Venue
from django import forms
from users.models import EmailCampaign, User


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
            "template": forms.Textarea(attrs={"rows": 30}),
        }

        help_texts = {
            "team_contestants": "Comma separated list of numbers.",
        }

    def __init__(self, competition: Competition, user: User, **kwargs):
        super().__init__(**kwargs)

        self.fields["team_countries"].choices = get_country_choices(competition, user)
        self.fields["team_languages"].choices = get_language_choices(competition.branch)
        self.fields["team_venues"].queryset = Venue.objects.for_user(competition, user)
