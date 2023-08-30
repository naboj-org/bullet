from datetime import datetime, timedelta

from django.utils import timezone
from problems.logic.results import add_result_row, fix_result_row
from problems.models import Problem, ResultRow, SolvedProblem
from users.models import Team


def get_last_problem_for_team(team: Team):
    return (
        SolvedProblem.objects.filter(team=team).count()
        + team.venue.category.problems_per_team
    )


def mark_problem_solved(
    team: Team,
    problem: Problem,
    timestamp: datetime | timedelta | None = None,
    repair_results: bool = True,
):
    if not timestamp:
        timestamp = timezone.now()
    sp = SolvedProblem(team=team, problem=problem)
    if isinstance(timestamp, datetime):
        sp.competition_time = timestamp - team.venue.start_time
    else:
        sp.competition_time = timestamp
    sp.save()

    add_result_row(team, sp.competition_time)
    if repair_results:
        fix_results(team, sp.competition_time)


def mark_problem_unsolved(
    team: Team, problem: Problem | SolvedProblem, repair_results: bool = True
):
    if isinstance(problem, SolvedProblem):
        sp = problem
    else:
        sp = SolvedProblem.objects.filter(team=team, problem=problem).first()
        if sp is None:
            return

    sp.delete()
    if repair_results:
        fix_results(team, sp.competition_time)


def fix_results(team: Team, after: timedelta | None = None):
    rows = ResultRow.objects.filter(team=team)
    if after:
        rows = rows.filter(competition_time__gte=after)

    for rr in rows:
        fix_result_row(rr)
