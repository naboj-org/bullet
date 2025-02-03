from django.db import models
from django.db.models import UniqueConstraint
from web.fields import LanguageField


class Problem(models.Model):
    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE, related_name="+"
    )
    number = models.PositiveIntegerField()


class CategoryProblem(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="category_problems"
    )
    category = models.ForeignKey(
        "competitions.Category",
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


class ProblemStat(models.Model):
    team = models.ForeignKey("users.Team", on_delete=models.CASCADE, related_name="+")
    problem = models.ForeignKey(Problem, on_delete=models.RESTRICT, related_name="+")
    received_time = models.DurationField()
    solved_time = models.DurationField(blank=True, null=True)
    solve_duration = models.DurationField(blank=True, null=True)


class ScannerLog(models.Model):
    class Result(models.IntegerChoices):
        OK = 0
        SCAN_ERR = 1
        INTEGRITY_ERR = 2

    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, blank=True, null=True
    )
    barcode = models.CharField(max_length=32)
    result = models.IntegerField(choices=Result.choices)
    message = models.CharField(max_length=128, blank=True)
    timestamp = models.DateTimeField()


class ResultRow(models.Model):
    team = models.ForeignKey("users.Team", on_delete=models.CASCADE, related_name="+")
    competition_time = models.DurationField()
    solved_problems = models.BinaryField()
    solved_count = models.IntegerField()

    def get_squares(self, problem_count, team_problem_count, first_problem):
        offset = first_problem - 1
        squares = []
        solved = int.from_bytes(self.solved_problems, "big")

        for i in range(problem_count):
            st = 0
            if solved & (1 << (i + offset)):
                st = 2
            elif i < self.solved_count + team_problem_count:
                st = 1

            squares.append(st)

        return squares


class ProblemStatement(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="statements"
    )
    language = LanguageField()
    statement = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    solution = models.TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                "problem", "language", name="problemstatement__problem_language"
            )
        ]
