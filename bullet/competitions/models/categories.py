from competitions.branches import Branches
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from web.fields import BranchField, ChoiceArrayField, LanguageField


class Category(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({Branches[self.branch]})"

    class Meta:
        constraints = [
            UniqueConstraint("branch", "slug", name="category__branch_slug"),
        ]


class CategoryDescription(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    language = LanguageField()
    countries = ChoiceArrayField(CountryField(blank=True, null=True))

    def __str__(self):
        return f"{self.name} ({self.language})"
