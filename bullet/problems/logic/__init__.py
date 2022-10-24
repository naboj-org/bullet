from datetime import datetime

from django.utils import timezone
from problems.models import CategoryProblem, Problem, ResultRow, SolvedProblem
from users.models import Team


def get_last_problem_for_team(team: Team):
    return (
        SolvedProblem.objects.filter(team=team).count()
        + team.venue.category_competition.problems_per_team
    )


def mark_problem_solved(team: Team, problem: Problem, timestamp: datetime = None):
    if not timestamp:
        timestamp = timezone.now()
    sp = SolvedProblem(team=team, problem=problem)
    sp.competition_time = timestamp - team.venue.start_time
    sp.save()

    problems = SolvedProblem.objects.filter(team=team)
    solved_problems = set(
        CategoryProblem.objects.filter(
            problem__in=problems, category=team.venue.category_competition
        ).values_list("number", flat=True)
    )

    result_row = ResultRow()
    result_row.team = team
    result_row.solved_count = len(solved_problems)

    solved_bin = 0
    for p in solved_problems:
        solved_bin |= 1 << (p - 1)

    result_row.solved_problems = solved_bin
    result_row.competition_time = sp.competition_time
    result_row.save()
