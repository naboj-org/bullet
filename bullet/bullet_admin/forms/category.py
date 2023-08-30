from django.forms import ModelForm

from competitions.models import CategoryCompetition


class CategoryForm(ModelForm):
    class Meta:
        model = CategoryCompetition

        fields = [
            "identifier",
            "order",
            "problems_per_team",
            "max_teams_per_school",
            "max_members_per_team",
            "max_teams_second_round",
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
