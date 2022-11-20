from bullet_admin.forms.utils import get_venue_queryset
from competitions.models import Competition, Venue
from django import forms
from documents.models import CertificateTemplate
from users.models import User


class CertificateForm(forms.Form):
    template = forms.ModelChoiceField(queryset=CertificateTemplate.objects.none())
    venue = forms.ModelChoiceField(queryset=Venue.objects.none())
    empty = forms.BooleanField()

    def __init__(self, competition: Competition, user: User, **kwargs):
        super().__init__(**kwargs)
        self.fields["template"].queryset = CertificateTemplate.objects.filter(
            branch=competition.branch
        ).order_by("name")
        self.fields["venue"].queryset = get_venue_queryset(competition, user)
