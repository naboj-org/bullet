from competitions.branches import Branches
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from web.fields import BranchField, ChoiceArrayField, LanguageField


class Page(models.Model):
    slug = models.SlugField(max_length=128)
    branch = BranchField()
    language = LanguageField()
    countries = ChoiceArrayField(CountryField())
    title = models.CharField(max_length=128)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Menu(models.Model):
    url = models.CharField(max_length=128)
    branch = BranchField()
    language = LanguageField()
    countries = ChoiceArrayField(CountryField())
    title = models.CharField(max_length=128)
    order = models.IntegerField(default=1)
    is_external = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Partner(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    image = models.FileField()


class Organizer(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    image = models.FileField()


class ContentBlock(models.Model):
    reference = models.CharField(max_length=256)
    branch = BranchField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    language = models.CharField(choices=settings.LANGUAGES, max_length=8)
    content = models.TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                ["reference", "branch", "country", "language"],
                name="ref_branch_country_lang_unique",
            )
        ]

    def __str__(self):
        if self.branch:
            branch = Branches[self.branch].short_name
            return f"{self.reference} ({branch} {self.country.code}-{self.language})"
        return f"{self.reference} ({self.country.code}-{self.language})"
