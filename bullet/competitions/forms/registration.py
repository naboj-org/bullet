from competitions.models import CategoryCompetition, Venue
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from education.models import School


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


class SchoolSelectForm(forms.Form):
    school = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self._country = kwargs.pop("venues")
        super().__init__(*args, **kwargs)

    def clean_school(self):
        school = self.cleaned_data["school"]

        obj = School.objects.filter(
            id=school,
        ).first()
        if obj is None:
            raise ValidationError(_("Selected school is not valid."))

        return school
