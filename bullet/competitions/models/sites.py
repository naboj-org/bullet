from address.models import AddressField
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Site(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256)
    address = AddressField()


class CompetitionSite(models.Model):
    category_competition = models.ForeignKey('competitions.CategoryCompetition', on_delete=models.CASCADE)
    site = models.ForeignKey('competitions.Site', on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(default=0)

    accepted_languages = ArrayField(base_field=models.IntegerField())
    local_start = models.DateTimeField(null=True, blank=True)
    results_announced = models.BooleanField(default=False)
    participants_hidden = models.BooleanField(default=False)
    email_alias = models.EmailField(null=True, blank=True)

    class Meta:
        unique_together = ('category_competition', 'site')
