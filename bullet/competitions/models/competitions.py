import functools
import secrets
from datetime import timedelta
from pathlib import Path

from bullet_admin.models import CompetitionRole
from competitions.branches import Branch
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from users.models import User
from web.fields import BranchField


def get_random_string():
    return secrets.token_hex(32)


class CompetitionQuerySet(models.QuerySet):
    def get_current_competition(self, branch):
        return (
            self.filter(branch=branch, web_start__lt=timezone.now())
            .order_by("-web_start")
            .first()
        )

    def for_request(self, request):
        """
        Filters competitions that should be visible for a given request.
        """
        return self.for_user(
            request.user,
            request.BRANCH,
        )

    def for_user(self, user: "User", branch: "Branch"):
        """
        Filters competitions that should be visible for a given user.
        """
        qs = self.filter(branch=branch).order_by("-web_start")

        if not user.is_authenticated:
            return qs.filter(results_public=True)

        # Branch admin can see all competitions
        if user.get_branch_role(branch).is_admin:
            return qs

        roles = CompetitionRole.objects.filter(
            user=user, competition__branch=branch
        ).values("competition")
        return qs.filter(id__in=roles)

    def for_photos(self, user: "User", branch: "Branch"):
        """
        Filters competitions that should be visible for a given user.
        """
        qs = self.filter(branch=branch).order_by("-web_start")

        if not user.is_authenticated:
            return qs.filter(results_public=True)

        branch_role = user.get_branch_role(branch)
        if branch_role.is_admin or branch_role.is_photographer:
            print(qs)
            return qs

        roles = CompetitionRole.objects.filter(
            user=user, competition__branch=branch
        ).values("competition")
        return qs.filter(id__in=roles)


class Competition(models.Model):
    name = models.CharField(max_length=128)
    branch = BranchField()
    number = models.IntegerField(
        null=True, blank=True
    )  # TODO: remove null when migrated on production
    secret_key = models.CharField(max_length=64, default=get_random_string)

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

    class Meta:
        constraints = [
            UniqueConstraint(
                "branch",
                "number",
                name="competition_branch_number_unique",
            )
        ]

    def __str__(self):
        return f'{self.name}{" (Cancelled)" if self.is_cancelled else ""}'

    @property
    def is_registration_open(self):
        return self.registration_start <= timezone.now() < self.registration_end

    @property
    def has_started(self):
        return self.competition_start <= timezone.now()

    @property
    def secret_dir(self) -> Path:
        return Path("competitions") / f"{self.id}-{self.secret_key}"

    @functools.total_ordering
    class State(models.IntegerChoices):
        BEFORE_WEB_START = (1, "Before web start")
        BEFORE_REGISTRATION = (2, "Before registration")
        REGISTRATION = (3, "Registration")
        AFTER_REGISTRATION = (4, "After registration")
        COMPETITION = (5, "Competition")
        AFTER_COMPETITION = (6, "After competition")
        LOCKED = (7, "Locked")

        def __lt__(self, other):
            if not isinstance(other, Competition.State):
                return NotImplemented
            return self.value < other.value

        def __eq__(self, other):
            if not isinstance(other, Competition.State):
                return NotImplemented
            return self.value == other.value

    @property
    def state(self) -> State:
        now = timezone.now()
        if self.web_start > now:
            return Competition.State.BEFORE_WEB_START
        if self.registration_start > now:
            return Competition.State.BEFORE_REGISTRATION
        if self.registration_end > now:
            return Competition.State.REGISTRATION
        if self.competition_start > now:
            return Competition.State.AFTER_REGISTRATION
        if self.competition_start + self.competition_duration > now:
            return Competition.State.COMPETITION
        if self.results_public:
            return Competition.State.LOCKED
        return Competition.State.AFTER_COMPETITION


class Category(models.Model):
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
                name="competitions_category_identifier_unique",
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
    competition = models.ForeignKey("competitions.Category", on_delete=models.CASCADE)
    school = models.ForeignKey("education.School", on_delete=models.CASCADE)
    note = models.TextField(blank=True)
