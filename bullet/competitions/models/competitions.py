from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from web.fields import BranchField


class CompetitionQuerySet(models.QuerySet):
    def currently_running_registration(self):
        now = timezone.now()
        return self.filter(
            registration_end__gte=now,
            registration_start__lte=now,
            is_cancelled=False,
        )

    def get_current_competition(self, branch):
        return self.filter(branch=branch).order_by("-web_start").first()


class Competition(models.Model):
    name = models.CharField(max_length=128)
    branch = BranchField()

    graduation_year = models.PositiveIntegerField()

    web_start = models.DateTimeField()

    registration_start = models.DateTimeField()
    registration_second_round_start = models.DateTimeField(null=True, blank=True)
    registration_end = models.DateTimeField()

    competition_start = models.DateTimeField()
    competition_duration = models.DurationField()

    is_cancelled = models.BooleanField(default=False)

    objects = CompetitionQuerySet.as_manager()

    def __str__(self):
        return f'{self.name}{" (Cancelled)" if self.is_cancelled else ""}'


class CategoryCompetitionQueryset(models.QuerySet):
    def registration_possible(self):
        return self.filter(
            competition__in=Competition.objects.currently_running_registration()
        )


class CategoryCompetition(models.Model):
    class RankingCriteria(models.IntegerChoices):
        SCORE = 1, _("Score")
        PROBLEMS = 2, _("Problems")
        TIME = 3, _("Time")

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

    ranking = ArrayField(
        base_field=models.PositiveIntegerField(choices=RankingCriteria.choices)
    )

    objects = CategoryCompetitionQueryset.as_manager()

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


class Wildcard(models.Model):
    competition = models.ForeignKey(
        "competitions.CategoryCompetition", on_delete=models.CASCADE
    )
    school = models.ForeignKey("education.School", on_delete=models.CASCADE)
    note = models.TextField(blank=True)
