from django.forms import forms, ModelForm, ModelChoiceField

from competitions.models import CompetitionSite
from users.models import Team


class RegistrationForm(ModelForm):
    def __init__(self, **kwargs):
        self.available_sites = kwargs.pop('available_sites')
        self.competition = kwargs.pop('competition')

        super().__init__(**kwargs)
        self.fields['competition_site'] = ModelChoiceField(
            queryset=self.available_sites
        )

    # TODO validate that the participants don't overlap between teams, that maximum team occupancy was not reached
    #  for a school, that seat occupancy  isn't reached for the venue

    class Meta:
        model = Team
        fields = ['contact_name', 'contact_email', 'contact_phone', 'school', 'language', 'competition_site']
