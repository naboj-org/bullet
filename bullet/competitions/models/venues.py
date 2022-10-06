from countries.models import BranchCountry
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django_countries.fields import CountryField
from users.models import Team
from web.fields import ChoiceArrayField, LanguageField


class CompetitionVenueQuerySet(models.QuerySet):
    def with_occupancy(self):
        return self.annotate(
            occupancy=Coalesce(
                Subquery(
                    Team.objects.filter(
                        confirmed_at__isnull=False, venue=OuterRef("pk")
                    )
                    .values("venue")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                Value(0),
            )
        )


class Venue(models.Model):
    name = models.CharField(max_length=256)
    shortcode = models.CharField(max_length=6)
    email = models.EmailField(blank=True, default="")
    address = models.CharField(max_length=256, blank=True)
    country = CountryField()

    category_competition = models.ForeignKey(
        "competitions.CategoryCompetition", on_delete=models.CASCADE
    )
    capacity = models.PositiveIntegerField(default=0)

    accepted_languages = ChoiceArrayField(LanguageField())
    local_start = models.DateTimeField(null=True, blank=True)
    results_announced = models.BooleanField(default=False)
    participants_hidden = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    objects = CompetitionVenueQuerySet.as_manager()

    class Meta:
        unique_together = ("category_competition", "shortcode")

    def __str__(self):
        return f"{self.name} ({self.category_competition.identifier})"

    @property
    def remaining_capacity(self):
        return self.capacity - self.team_set.count()

    @property
    def contact_email(self):
        if not self.email:
            return BranchCountry.objects.get(
                branch=self.category_competition.competition.branch,
                country=self.country,
            ).email
        return self.email
