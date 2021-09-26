from django.conf import settings
from django.db import models

from bullet.constants import Languages


class Problem(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class LocalizedProblem(models.Model):
    problem = models.ForeignKey('competitions.Problem', on_delete=models.CASCADE)
    language = models.TextField(choices=Languages.choices)
    statement_text = models.TextField()
    result_text = models.TextField()
    solution_text = models.TextField()

    class Meta:
        unique_together = ('problem', 'language')


class CompetitionProblem(models.Model):
    category_competition = models.ForeignKey('competitions.CategoryCompetition', on_delete=models.CASCADE)
    problem = models.ForeignKey('competitions.Problem', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('category_competition', 'number')

    def __str__(self):
        return f'#{self.number} {self.problem} in {self.category_competition}'


class SolutionSubmitLog(models.Model):
    problem = models.ForeignKey('competitions.CompetitionProblem', on_delete=models.CASCADE)
    team = models.ForeignKey('users.Team', on_delete=models.CASCADE)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
