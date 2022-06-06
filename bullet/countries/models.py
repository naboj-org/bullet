from competitions.models import BranchField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_countries.fields import CountryField


class BranchCountry(models.Model):
    branch = BranchField()
    country = CountryField()
    languages = ArrayField(base_field=models.CharField(max_length=8))
