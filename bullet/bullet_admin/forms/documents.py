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


class TearoffForm(forms.Form):
    problems = forms.FileField(
        label="Problem file",
        help_text=(
            "A PDF file containing one problem per page (including last empty page)."
        ),
    )
    first_problem = forms.IntegerField(
        label="First problem",
        initial=1,
        min_value=1,
    )
    backup_teams = forms.IntegerField(
        label="Number of backup teams",
        initial=0,
        min_value=0,
    )
    ordering = forms.ChoiceField(
        label="Problem ordering",
        choices=[("align", "Aligned"), ("seq", "Sequential")],
    )
