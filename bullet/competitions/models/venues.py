from address.models import AddressField
from countries.models import BranchCountry
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django_countries.fields import CountryField
from users.models import Team
from web.fields import ChoiceArrayField, LanguageField


class Venue(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256)
    address = AddressField()
    country = CountryField()
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} at {self.address}"


class CompetitionVenueQuerySet(models.QuerySet):
    def with_occupancy(self):
        return self.annotate(
            occupancy=Coalesce(
                Subquery(
                    Team.objects.filter(
                        confirmed_at__isnull=False, competition_venue=OuterRef("pk")
                    )
                    .values("competition_venue")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                Value(0),
            )
        )


class CompetitionVenue(models.Model):
    category_competition = models.ForeignKey(
        "competitions.CategoryCompetition", on_delete=models.CASCADE
    )
    venue = models.ForeignKey("competitions.Venue", on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(default=0)

    accepted_languages = ChoiceArrayField(LanguageField())
    local_start = models.DateTimeField(null=True, blank=True)
    results_announced = models.BooleanField(default=False)
    participants_hidden = models.BooleanField(default=False)
    email = models.EmailField(blank=True, default="")

    objects = CompetitionVenueQuerySet.as_manager()

    class Meta:
        unique_together = ("category_competition", "venue")

    def __str__(self):
        return f"{self.venue.name} hosting {self.category_competition}"

    @property
    def remaining_capacity(self):
        return self.capacity - self.team_set.count()

    @property
    def contact_email(self):
        if not self.email:
            return BranchCountry.objects.get(
                branch=self.category_competition.competition.branch,
                country=self.venue.country,
            ).email
        return self.email
