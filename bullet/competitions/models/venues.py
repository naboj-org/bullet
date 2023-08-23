from typing import TYPE_CHECKING

from bullet_admin.utils import get_active_competition
from countries.models import BranchCountry
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django_countries.fields import CountryField
from users.models import Team
from web.fields import ChoiceArrayField, LanguageField

if TYPE_CHECKING:
    from competitions.models import Competition
    from users.models import User


class VenueQuerySet(models.QuerySet):
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

    def for_competition(self, competition):
        return self.filter(category_competition__competition=competition)

    def for_request(self, request):
        """
        Filters venues that should be visible for a given request.
        """
        return self.for_user(
            get_active_competition(request),
            request.user,
        )

    def for_user(self, competition: "Competition", user: "User"):
        """
        Filters venues that should be visible for a given user.
        """
        qs = self.for_competition(competition)

        if not user.is_authenticated:
            return self.none()

        # Branch admin can see all venues
        if user.get_branch_role(competition.branch).is_admin:
            return qs

        # Competition admin can see all venues of his country
        # or just his venues
        crole = user.get_competition_role(competition)
        if crole.countries:
            qs = qs.filter(country__in=crole.countries)
        if crole.venues:
            qs = qs.filter(id__in=crole.venues)

        # Non-admins cannot see anything
        if not crole.venues and not crole.countries:
            return self.none()

        return qs


class VenueManager(models.Manager):
    def get_queryset(self):
        return VenueQuerySet(self.model, using=self._db).select_related(
            "category_competition"
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
    is_reviewed = models.BooleanField(default=False)

    objects = VenueManager.from_queryset(VenueQuerySet)()

    class Meta:
        unique_together = ("category_competition", "shortcode")
        ordering = ("name", "category_competition__identifier")

    def __str__(self):
        return f"{self.name} ({self.category_competition.identifier})"

    @property
    def remaining_capacity(self):
        return self.capacity - Team.objects.competing().filter(venue=self).count()

    @property
    def contact_email(self):
        if not self.email:
            return BranchCountry.objects.get(
                branch=self.category_competition.competition.branch,
                country=self.country,
            ).email
        return self.email

    @property
    def start_time(self):
        if self.local_start:
            return self.local_start
        return self.category_competition.competition.competition_start
