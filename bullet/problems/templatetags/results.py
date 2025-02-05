from typing import Optional

from competitions.models import Competition, Venue
from competitions.models.competitions import Category
from django import template

from problems.models import ResultRow

register = template.Library()


@register.inclusion_tag("problems/results/squares.html")
def squares(
    obj: ResultRow,
    problem_count: Optional[int] = None,
    team_problem_count: Optional[int] = None,
    first_problem: Optional[int] = None,
    big: bool = False,
):
    category: Category = obj.team.venue.category
    if not team_problem_count:
        team_problem_count = category.problems_per_team
    if not first_problem:
        first_problem = category.first_problem
    if not problem_count:
        problem_count = category.competition.problem_count - first_problem + 1

    squares = obj.get_squares(problem_count, team_problem_count, first_problem)
    squares_grouped = []
    for i in range(0, len(squares), 5):
        group = []
        for idx in range(i, i + 5):
            if len(squares) <= idx:
                continue
            group.append({"problem": idx + first_problem, "state": squares[idx]})
        squares_grouped.append(group)

    return {
        "squares": squares_grouped,
        "big": big,
    }


@register.inclusion_tag("problems/results/squares.html")
def big_squares(
    obj: ResultRow,
    problem_count: Optional[int] = None,
    team_problem_count: Optional[int] = None,
    first_problem: Optional[int] = None,
):
    ctx = squares(obj, problem_count, team_problem_count, first_problem, True)
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
