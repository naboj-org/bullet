from django.db import models
from django.db.models import UniqueConstraint


class Problem(models.Model):
    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)


class CategoryProblem(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    category = models.ForeignKey(
        "competitions.CategoryCompetition", on_delete=models.CASCADE
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
