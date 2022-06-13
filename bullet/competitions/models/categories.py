from competitions.branches import Branches
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_countries.fields import CountryField
from web.fields import BranchField, LanguageField


class Category(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} ({Branches[self.branch]})"


class CategoryDescription(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    language = LanguageField()
    countries = ArrayField(base_field=CountryField(blank=True, null=True))

    def __str__(self):
        return f"{self.name} ({self.language})"
