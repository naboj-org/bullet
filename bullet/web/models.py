import os.path

from competitions.branches import Branches
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
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


def logo_upload_path(instance: "Logo", filename):
    _, ext = os.path.splitext(filename)
    return f"logos/{Branches[instance.branch].identifier}/{slugify(instance.name)}{ext}"


class LogoQuerySet(models.QuerySet):
    def partners(self):
        return self.filter(type=Logo.Type.PARTNER)

    def organizers(self):
        return self.filter(type=Logo.Type.ORGANIZER)

    def for_branch_country(self, branch, country):
        return self.filter(branch=branch, countries__contains=[country.upper()])


class Logo(models.Model):
    class Type(models.IntegerChoices):
        ORGANIZER = 0
        PARTNER = 1

    branch = BranchField()
    type = models.IntegerField(choices=Type.choices)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    image = models.FileField(upload_to=logo_upload_path)
    countries = ChoiceArrayField(CountryField())

    objects = LogoQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} ({Branches[self.branch].name})"


class ContentBlock(models.Model):
    group = models.CharField(max_length=256)
    reference = models.CharField(max_length=256)
    branch = BranchField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    language = models.CharField(choices=settings.LANGUAGES, max_length=8)
    content = models.TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("group", "reference", "branch", "country", "language"),
                name="content_block__reference_unique",
            )
        ]

    def __str__(self):
        prefix = f"{self.group}:{self.reference} "
        if self.branch:
            branch = Branches[self.branch].short_name
            return prefix + f"({branch} {self.country.code}-{self.language})"
        return prefix + f"({self.country.code}-{self.language})"
