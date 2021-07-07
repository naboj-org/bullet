from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import IntegerChoices
from django.utils.translation import ugettext_lazy as _


class Competition(models.Model):
    class Branch(IntegerChoices):
        MATH = 1, _('Math')
        PHYSICS = 2, _('Physics')
        JUNIOR = 3, _('Junior')

    name = models.CharField(max_length=128)
    branch = models.IntegerField(choices=Branch.choices)

    graduation_year = models.PositiveIntegerField()

    web_start = models.DateTimeField()

    registration_start = models.DateTimeField()
    registration_second_round_start = models.DateTimeField(null=True)
    registration_end = models.DateTimeField()

    competition_start = models.DateTimeField()
    competition_duration = models.DurationField()

    is_cancelled = models.BooleanField(default=False)


class CategoryCompetition(models.Model):
    class Category(IntegerChoices):
        SENIOR = 1, _('Senior')
        JUNIOR = 2, _('Junior')
        CADET = 3, _('Cadet')
        OPEN = 4, _('Open')

    class RankingCriteria(models.IntegerChoices):
        SCORE = 1, _('Score')
        PROBLEMS = 2, _('Problems')
        TIME = 3, _('Time')

    competition = models.ForeignKey('competitions.Competition', on_delete=models.CASCADE)
    category = models.IntegerField(choices=Category.choices)

    problems_per_team = models.PositiveIntegerField(null=True)
    max_teams_per_school = models.PositiveIntegerField(null=True)
    max_teams_second_round = models.PositiveIntegerField(null=True)
    max_members_per_team = models.PositiveIntegerField(null=True)

    ranking = ArrayField(base_field=models.PositiveIntegerField(choices=RankingCriteria.choices))

    class Meta:
        unique_together = ('competition', 'category')


class Wildcard(models.Model):
    competition = models.ForeignKey('competitions.CategoryCompetition', on_delete=models.CASCADE)
    school = models.ForeignKey('users.School', on_delete=models.CASCADE)
    note = models.TextField(blank=True)
