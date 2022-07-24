from competitions.models import CategoryCompetition, Venue
from django import forms


class CategorySelectForm(forms.Form):
    category_competition = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        categories: list[CategoryCompetition] = kwargs.pop("categories")
        super().__init__(*args, **kwargs)
        self.fields["category_competition"].choices = [
            (c.id, str(c)) for c in categories
        ]


class VenueSelectForm(forms.Form):
    venue = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        venues: list[Venue] = kwargs.pop("venues")
        super(VenueSelectForm, self).__init__(*args, **kwargs)
        self.fields["venue"].choices = [(v.id, str(v)) for v in venues]
