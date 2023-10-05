from competitions.models import Category
from django.forms import ModelForm


class CategoryForm(ModelForm):
    class Meta:
        model = Category

        fields = [
            "identifier",
            "order",
            "problems_per_team",
            "max_members_per_team",
            "max_teams_per_school",
            "max_teams_second_round",
        ]

        labels = {
            "problems_per_team": "Available problems",
            "max_members_per_team": "Max. number of team members",
            "max_teams_per_school": "Max. number of teams per school",
            "max_teams_second_round": "Max. number of teams per school (2nd round)",
        }

        help_texts = {
            "identifier": "Lowercase name of the category used internally by the "
            "system.",
            "order": "Categories are sorted by this number in ascending order when "
            "displayed.",
            "problems_per_team": "The number of problems a team has at any given time.",
            "max_teams_per_school": "Any additional teams will be placed on the "
            "waiting list. This only applies during the 1st round of registration.",
            "max_teams_second_round": "See above. This only applies during the 2nd "
            "round of registration.",
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
