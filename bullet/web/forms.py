from django.utils.translation import get_language
from django.forms import forms, ModelForm, ModelChoiceField, inlineformset_factory

from bullet.constants import PHONE_REGIONS
from competitions.models import CompetitionSite
from users.models import Team, Participant
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible


class RegistrationForm(ModelForm):
    def __init__(self, **kwargs):
        self.available_sites = kwargs.pop('available_sites')
        self.competition = kwargs.pop('competition')

        super().__init__(**kwargs)
        self.fields['competition_site'] = ModelChoiceField(
            queryset=self.available_sites
        )
        self.fields['contact_phone'].region = PHONE_REGIONS[get_language()]


    # TODO validate that the participants don't overlap between teams, that maximum team occupancy was not reached
    #  for a school, that seat occupancy  isn't reached for the venue

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
