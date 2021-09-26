from address.models import AddressField
from django.contrib.postgres.fields import ArrayField
from django.db import models

from bullet.constants import Languages
from django.db.models import Subquery, OuterRef, Count, Value
from django.db.models.functions import Coalesce

from users.models import Team, Participant


class Site(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256)
    address = AddressField(null=True)

    def __str__(self):
        return f'{self.name} at {self.address}'


class CompetitionSiteQuerySet(models.QuerySet):
    def with_occupancy(self):
        return self.annotate(
            occupancy=Coalesce(
                Subquery(
                    Participant.objects.filter(team__competition_site=OuterRef('pk')).values(
                        'team__competition_site').annotate(count=Count('pk')).values('count')
                ),
                Value(0)
            )
        )


class CompetitionSite(models.Model):
    category_competition = models.ForeignKey('competitions.CategoryCompetition', on_delete=models.CASCADE)
    site = models.ForeignKey('competitions.Site', on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(default=0)

    accepted_languages = ArrayField(base_field=models.CharField(choices=Languages.choices, max_length=10))
    local_start = models.DateTimeField(null=True, blank=True)
    results_announced = models.BooleanField(default=False)
    participants_hidden = models.BooleanField(default=False)
    email_alias = models.EmailField(null=True, blank=True)

    objects = CompetitionSiteQuerySet.as_manager()

    class Meta:
        unique_together = ('category_competition', 'site')

    def __str__(self):
        return f'{self.site.name} hosting {self.category_competition}'
