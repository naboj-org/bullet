from django.db import models
from django.db.models import UniqueConstraint


class Problem(models.Model):
    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE, related_name="+"
    )
    name = models.CharField(max_length=128)


class CategoryProblem(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="category_problems"
    )
    category = models.ForeignKey(
        "competitions.CategoryCompetition",
        on_delete=models.CASCADE,
        related_name="problems",
    )
    number = models.PositiveIntegerField()

    class Meta:
        constraints = (
            UniqueConstraint(
                "problem",
                "category",
                "number",
                name="categoryproblem__problem_category_number",
            ),
        )


class SolvedProblem(models.Model):
    team = models.ForeignKey(
        "users.Team", on_delete=models.CASCADE, related_name="solved_problems"
    )
    problem = models.ForeignKey(Problem, on_delete=models.RESTRICT, related_name="+")
    competition_time = models.DurationField()
