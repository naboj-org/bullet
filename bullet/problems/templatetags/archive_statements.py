from datetime import timedelta
from typing import Iterable

from competitions.models.competitions import Category
from django import template

from problems.models import ProblemStatement

register = template.Library()


@register.simple_tag()
def problem_number(problem: ProblemStatement, categories: Iterable[Category]):
    numbers = []
    used_numbers = set()

    for cat in categories:
        prefix = cat.identifier[0].upper()
        number = problem.problem.number + 1 - cat.first_problem
        numbers.append((prefix, number))
        used_numbers.add(number)

    if len(used_numbers) == 1:
        return used_numbers.pop()

    return " / ".join([f"{n[0]}{n[1]}" for n in numbers if n[1] >= 1])


@register.filter()
def timedelta_format(td: timedelta):
    if not td:
        return "-"

    total = td.total_seconds()
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)

    return ":".join([f"{int(x):02d}" for x in (hours, minutes, seconds)])


@register.filter()
def problem_solve_percentage(stats):
    if not stats["received"]:
    	return "-"
    per = stats["solved"] / stats["received"]
    per = round(per * 100, 1)
    return f"{per:0.1f}"
