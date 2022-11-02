from datetime import timedelta

from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from web.fields import BranchField


class CompetitionQuerySet(models.QuerySet):
    def get_current_competition(self, branch):
        return self.filter(branch=branch).order_by("-web_start").first()


class Competition(models.Model):
    name = models.CharField(max_length=128)
    branch = BranchField()

    web_start = models.DateTimeField()

    registration_start = models.DateTimeField()
    registration_second_round_start = models.DateTimeField(null=True, blank=True)
    registration_end = models.DateTimeField()

    competition_start = models.DateTimeField()
    competition_duration = models.DurationField()
    results_freeze = models.DurationField(
        default=timedelta(),
        help_text="How long before the competition end should we freeze the results.",
    )
    results_public = models.BooleanField(default=False)

    is_cancelled = models.BooleanField(default=False)

    objects = CompetitionQuerySet.as_manager()

    def __str__(self):
        return f'{self.name}{" (Cancelled)" if self.is_cancelled else ""}'

    @property
    def is_registration_open(self):
        return self.registration_start <= timezone.now() < self.registration_end

    @property
    def has_started(self):
        return self.competition_start <= timezone.now()


class CategoryCompetition(models.Model):
    competition = models.ForeignKey(
        "competitions.Competition",
        on_delete=models.CASCADE,
    )

    identifier = models.SlugField()
    order = models.IntegerField(default=0)

    educations = models.ManyToManyField("education.Education")

    problems_per_team = models.PositiveIntegerField()
    max_teams_per_school = models.PositiveIntegerField()
    max_teams_second_round = models.PositiveIntegerField()
    max_members_per_team = models.PositiveIntegerField()

    class Meta:
        constraints = (
            UniqueConstraint(
                "competition",
                "identifier",
                name="competitions_category_competition_identifier_unique",
            ),
        )
        ordering = ("order",)

    def __str__(self):
        return f"{self.identifier} ({self.competition.name})"

    def max_teams_per_school_at(self, time):
        competition = self.competition
        if (
            competition.registration_second_round_start
            and competition.registration_second_round_start <= time
        ):
            return self.max_teams_second_round
        return self.max_teams_per_school


class Wildcard(models.Model):
    competition = models.ForeignKey(
        "competitions.CategoryCompetition", on_delete=models.CASCADE
    )
    school = models.ForeignKey("education.School", on_delete=models.CASCADE)
    note = models.TextField(blank=True)
