from competitions.models import Competition, Venue
from django import forms
from documents.models import CertificateTemplate
from users.models import User


class CertificateForm(forms.Form):
    template = forms.ModelChoiceField(queryset=CertificateTemplate.objects.none())
    count = forms.IntegerField(
        initial=3,
        help_text="Enter 0 to generate certificates for all teams.",
        min_value=0,
    )
    empty = forms.BooleanField(required=False)

    def __init__(self, competition: Competition, **kwargs):
        super().__init__(**kwargs)
        self.fields["template"].queryset = CertificateTemplate.objects.filter(
            branch=competition.branch
        ).order_by("name")


class TeamListForm(forms.Form):
    venue = forms.ModelChoiceField(queryset=Venue.objects.none())

    def __init__(self, competition: Competition, user: User, **kwargs):
        super().__init__(**kwargs)
        self.fields["venue"].queryset = Venue.objects.for_user(competition, user)
