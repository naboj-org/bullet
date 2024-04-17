from typing import Optional

from competitions.models import Competition, Venue
from django import template

from problems.models import ResultRow

register = template.Library()


@register.inclusion_tag("problems/results/squares.html")
def squares(
    obj: ResultRow,
    problem_count: Optional[int] = None,
    team_problem_count: Optional[int] = None,
    first_problem: Optional[int] = None,
):
    if not team_problem_count:
        team_problem_count = obj.team.venue.category.problems_per_team
    if not first_problem:
        first_problem = obj.team.venue.category.first_problem
    if not problem_count:
        problem_count = obj.team.venue.category.problems.count()

    return {
        "squares": obj.get_squares(problem_count, team_problem_count, first_problem),
        "offset": first_problem - 1,
    }


@register.inclusion_tag("problems/results/squares.html")
def big_squares(
    obj: ResultRow,
    problem_count: Optional[int] = None,
    team_problem_count: Optional[int] = None,
    first_problem: Optional[int] = None,
):
    ctx = squares(obj, problem_count, team_problem_count, first_problem)
    ctx["big"] = True
    return ctx


@register.inclusion_tag("problems/results/timer.html")
def venue_timer(venue: Venue | str, competition: Competition):
    if isinstance(venue, str):
        venue = (
            Venue.objects.for_competition(competition).filter(shortcode=venue).first()
        )

    return {
        "start_time": venue.start_time if venue else competition.competition_start,
        "duration": competition.competition_duration,
    }
