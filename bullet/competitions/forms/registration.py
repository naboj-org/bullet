from typing import Iterable

from bullet_admin.forms.utils import get_language_choices_for_venue
from countries.logic.country import get_country
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible
from education.models import Grade, School, SchoolType
from users.models import Contestant, SpanishTeamData, Team

from competitions.models import Category, Venue


class CategorySelectForm(forms.Form):
    category = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        categories: list[Category] = kwargs.pop("categories")
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [(c.id, str(c)) for c in categories]


class VenueSelectForm(forms.Form):
    venue = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        venues: list[Venue] = kwargs.pop("venues")
        super(VenueSelectForm, self).__init__(*args, **kwargs)
        self.fields["venue"].choices = [(v.id, v.name) for v in venues]


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
            # Translators: This is a rare error that occurs when the user selects
            # a school that we don't have in our database.
            raise ValidationError(_("Selected school is not valid."))

        return school


class RegistrationForm(ModelForm):
    def __init__(self, venue, **kwargs):
        super().__init__(**kwargs)
        self.fields["contact_phone"].widget.region = get_country().upper()

        choices = get_language_choices_for_venue(venue)
        self.fields["language"].choices = choices
        self.fields["language"].initial = get_language()

        if len(choices) == 1:
            self.fields["language"].widget = forms.HiddenInput()

    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "language",
        ]
        labels = {
            "contact_name": _("Full name"),
            "contact_email": _("Email"),
            "contact_phone": _("Phone number"),
            "language": _("Language"),
        }
        help_texts = {
            "language": _(
                "You will receive problem statements in the language you choose."
            ),
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
        self.category: Category = kwargs.pop("category")
        super().__init__(**kwargs)

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
        grade_obj = Grade.objects.filter(
            id=grade, education__category=self.category
        ).first()

        if grade_obj is None:
            raise ValidationError(_("This grade can't compete in the chosen category."))

        return grade_obj


def file_size(file):
    if file.size > 10_000_000:
        raise ValidationError(_("The uploaded file is too large."))


class SpanishRegistrationForm(RegistrationForm):
    agreement = forms.FileField(
        validators=[FileExtensionValidator(["pdf", "zip"]), file_size],
        label="Autorizaciones",
        help_text=mark_safe(
            "Envíe un <b>único documento PDF</b> con <b>todas las autorizaciones "
            "cumplimentadas al completo y firmadas. En caso de firmas digitales "
            "(y sólo en ese caso)</b> aceptamos ZIPs que contengan <b>todas</b> "
            "las autorizaciones del equipo. El <b>link</b> a la <b>autorización</b> "
            "se encuentra más <b>abajo</b>."
        ),
        required=True,
    )

    def save_related(self):
        d = SpanishTeamData(team=self.instance)
        d.agreement = self.cleaned_data.get("agreement")
        d.save()
