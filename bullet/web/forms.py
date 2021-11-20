from django.core.exceptions import ValidationError
from django.utils.translation import get_language
from django.forms import ModelForm, ModelChoiceField, inlineformset_factory

from bullet.constants import PHONE_REGIONS
from competitions.models import CategoryCompetition, CompetitionSite
from users.models import Team, Participant
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible


class RegistrationForm(ModelForm):
    def __init__(self, **kwargs):
        self.available_sites = kwargs.pop('available_sites')
        self.category_competition: CategoryCompetition = kwargs.pop('category_competition')

        super().__init__(**kwargs)
        self.fields['competition_site'] = ModelChoiceField(
            queryset=self.available_sites
        )
        self.fields['contact_phone'].region = PHONE_REGIONS[get_language()]

    def clean_school(self):
        data = self.cleaned_data['school']

        same_school_teams_count = Team.objects.filter(
            competition_site__category_competition=self.category_competition,
            confirmed_at__isnull=False
        ).count()

        if same_school_teams_count >= self.category_competition.max_teams_per_school:
            raise ValidationError(f'Registered teams limit for this school has been reached ( max {self.category_competition.max_teams_per_school} per school)')

        return data

    def clean_competition_site(self):
        data = self.cleaned_data['competition_site']

        same_site_teams_count = Team.objects.filter(competition_site=data).filter(confirmed_at__isnull=False).count()
        if same_site_teams_count >= data.capacity:
            raise ValidationError(f'Full occupancy for this competition venue has been reached')

        return data

    class Meta:
        model = Team
        fields = ['contact_name', 'contact_email', 'contact_phone', 'school', 'language', 'competition_site']

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)


ParticipantsFormSet = inlineformset_factory(
    Team,
    Participant,
    min_num=1,
    fields=('first_name', 'last_name', 'graduation_year', 'birth_year')
)
