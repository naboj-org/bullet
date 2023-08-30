from competitions.models import Category
from django.forms import ModelForm


class CategoryForm(ModelForm):
    class Meta:
        model = Category

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
