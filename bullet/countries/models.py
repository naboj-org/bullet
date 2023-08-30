from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint
from django_countries.fields import CountryField
from timezone_field import TimeZoneField
from web.fields import BranchField, ChoiceArrayField, LanguageField


class BranchCountry(models.Model):
    branch = BranchField()
    country = CountryField()
    languages = ChoiceArrayField(LanguageField())
    timezone = TimeZoneField()
    email = models.EmailField()
    hidden_languages = ChoiceArrayField(LanguageField(), blank=True, default=list)

    class Meta:
        constraints = [
            UniqueConstraint("branch", "country", name="branch_country_unique"),
            CheckConstraint(
                check=Q(languages__contains=F("hidden_languages")),
                name="hidden_languages_in_languages",
            ),
        ]
