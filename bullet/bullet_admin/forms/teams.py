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
        ]

    def __init__(self, **kwargs):
        competition: Competition = kwargs.pop("competition")
        super().__init__(**kwargs)

        self.fields["venue"].queryset = Venue.objects.filter(
            category_competition__competition=competition
        ).select_related("category_competition")