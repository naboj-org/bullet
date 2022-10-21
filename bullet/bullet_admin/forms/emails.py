from bullet_admin.forms.utils import get_country_choices, get_language_choices
from competitions.models import Competition, Venue
from django import forms
from users.models import EmailCampaign


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
        )

        widgets = {
            "team_countries": forms.CheckboxSelectMultiple(),
            "team_languages": forms.CheckboxSelectMultiple(),
            "team_venues": forms.CheckboxSelectMultiple(),
            "team_statuses": forms.CheckboxSelectMultiple(),
            "template": forms.Textarea(attrs={"rows": 30}),
        }

    def __init__(self, competition: Competition, **kwargs):
        super().__init__(**kwargs)

        self.fields["team_countries"].choices = get_country_choices(competition.branch)
        self.fields["team_languages"].choices = get_language_choices(competition.branch)
        self.fields["team_venues"].queryset = (
            Venue.objects.filter(category_competition__competition=competition)
            .select_related("category_competition")
            .order_by("name", "category_competition__identifier")
        )
