from competitions.models import Competition, Venue
from django import forms
from users.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "school",
            "venue",
            "is_checked_in",
            "consent_photos",
        ]

    def __init__(self, **kwargs):
        competition: Competition = kwargs.pop("competition")
        super().__init__(**kwargs)

        self.fields["venue"].queryset = Venue.objects.filter(
            category_competition__competition=competition
        ).select_related("category_competition")
        self.fields["school"].required = True


class OperatorTeamForm(TeamForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.pop("school")
        self.fields.pop("venue")
        self.fields.pop("contact_name")
        self.fields.pop("contact_email")
        self.fields.pop("contact_phone")
