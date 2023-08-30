from competitions.models import Competition
from django.forms import DateTimeInput, ModelForm
from users.models import User


class CompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = [
            "name",
            "number",
            "web_start",
            "registration_start",
            "registration_second_round_start",
            "registration_end",
            "competition_start",
            "competition_duration",
            "results_freeze",
            "is_cancelled",
        ]

        help_texts = {
            "name": "Name of the competition",
            "web_start": "Date from when the competition will be shown on homepage",
            "results_freeze": "How long before the competition "
            "end the result table freezes",
        }

        labels = {"is_cancelled": "Cancel the competition?", "number": "Year"}

        widgets = {
            "web_start": DateTimeInput(attrs={"type": "datetime"}),
            "registration_start": DateTimeInput(attrs={"type": "datetime"}),
            "registration_second_round_start": DateTimeInput(
                attrs={"type": "datetime"}
            ),
            "registration_end": DateTimeInput(attrs={"type": "datetime"}),
            "competition_start": DateTimeInput(attrs={"type": "datetime"}),
        }

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
