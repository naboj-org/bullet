from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from competitions.models import CategoryCompetition
from countries.logic.country import get_country
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, inlineformset_factory
from users.models import Participant, Team


class RegistrationForm(ModelForm):
    def __init__(self, **kwargs):
        self.available_sites = kwargs.pop("available_sites")
        self.category_competition: CategoryCompetition = kwargs.pop(
            "category_competition"
        )

        super().__init__(**kwargs)
        self.fields["competition_venue"] = ModelChoiceField(
            queryset=self.available_sites
        )
        self.fields["contact_phone"].region = get_country()

    def clean_school(self):
        data = self.cleaned_data["school"]

        same_school_teams_count = Team.objects.filter(
            competition_venue__category_competition=self.category_competition,
            confirmed_at__isnull=False,
        ).count()

        if same_school_teams_count >= self.category_competition.max_teams_per_school:
            raise ValidationError(
                "Registered teams limit for this school has been reached ( max"
                f" {self.category_competition.max_teams_per_school} per school)"
            )

        return data

    def clean_competition_venue(self):
        data = self.cleaned_data["competition_venue"]

        same_site_teams_count = (
            Team.objects.filter(competition_venue=data)
            .filter(confirmed_at__isnull=False)
            .count()
        )
        if same_site_teams_count >= data.capacity:
            raise ValidationError(
                "Full occupancy for this competition venue has been reached"
            )

        return data

    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "school",
            "language",
            "competition_venue",
        ]

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)


ParticipantsFormSet = inlineformset_factory(
    Team,
    Participant,
    min_num=1,
    fields=("full_name", "graduation_year", "birth_year"),
)
