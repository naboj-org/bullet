from datetime import datetime

from django.utils import timezone
from problems.logic.results import add_result_row, fix_result_row
from problems.models import Problem, ResultRow, SolvedProblem
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

    add_result_row(team, sp.competition_time)


def mark_problem_unsolved(team: Team, problem: Problem):
    sp = SolvedProblem.objects.filter(team=team, problem=problem).first()
    if sp is None:
        return

    sp.delete()
    rows = ResultRow.objects.filter(
        team=team, competition_time__gte=sp.competition_time
    )
    for rr in rows:
        fix_result_row(rr)
