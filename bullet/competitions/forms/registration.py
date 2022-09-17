from typing import Iterable

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from competitions.models import CategoryCompetition, CompetitionVenue
from countries.logic.country import get_country
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext as _
from education.models import Grade, School, SchoolType
from users.models import Contestant, Team


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
        venues: list[CompetitionVenue] = kwargs.pop("venues")
        super(VenueSelectForm, self).__init__(*args, **kwargs)
        self.fields["venue"].choices = [(v.id, str(v.venue)) for v in venues]


class SchoolSelectForm(forms.Form):
    school = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self._country = kwargs.pop("country")
        super().__init__(*args, **kwargs)

    def clean_school(self):
        school = self.cleaned_data["school"]

        obj = School.objects.filter(
            id=school,
        ).first()
        if obj is None:
            raise ValidationError(_("Selected school is not valid."))

        return school


class RegistrationForm(ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["contact_phone"].widget.region = get_country().upper()

    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
        ]
        labels = {
            "contact_name": _("Full name"),
            "contact_email": _("Email"),
            "contact_phone": _("Phone number"),
        }

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)


class ContestantForm(ModelForm):
    grade = forms.ChoiceField()

    class Meta:
        model = Contestant
        fields = [
            "full_name",
            "grade",
        ]

    def __init__(self, **kwargs):
        school_types: Iterable[SchoolType] = kwargs.pop("school_types")
        super().__init__(**kwargs)

        # TODO: Limit choices to allowed Educations.
        grades = [("", _("(Please select)"))]
        for school_type in school_types:
            options = [
                (g.id, g.name)
                for g in sorted(school_type.grades.all(), key=lambda x: x.order)
            ]
            grades.append((school_type.name, options))

        self.fields["grade"].choices = grades

    def clean_grade(self):
        grade = self.cleaned_data["grade"]
        grade_obj = Grade.objects.filter(id=grade).first()

        if grade_obj is None:
            raise ValidationError(_("Please select a valid grade."))

        return grade_obj
