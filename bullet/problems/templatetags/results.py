from django import template
from problems.models import ResultRow

register = template.Library()


@register.inclusion_tag("problems/results/squares.html")
def squares(obj: ResultRow, problem_count: int, team_problem_count: int):
    return {"squares": obj.get_squares(problem_count, team_problem_count)}
