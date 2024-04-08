from competitions.models import Competition, Venue
from django import template

from problems.models import ResultRow

register = template.Library()


@register.inclusion_tag("problems/results/squares.html")
def squares(
    obj: ResultRow, problem_count: int, team_problem_count: int, first_problem: int
):
    return {
        "squares": obj.get_squares(problem_count, team_problem_count, first_problem),
        "offset": first_problem - 1,
    }


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
