from datetime import datetime

from django.utils import timezone
from problems.models import Problem, SolvedProblem
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
