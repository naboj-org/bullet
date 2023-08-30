from collections import defaultdict
from datetime import timedelta
from typing import Iterable

from django import template
from problems.models import CategoryProblem, ProblemStatement

register = template.Library()


@register.filter()
def problem_number(obj: ProblemStatement):
    problems: Iterable[CategoryProblem] = obj.problem.category_problems.all()
    numbers = set([cp.number for cp in problems])
    if len(numbers) == 1:
        return numbers.pop()

    number_category: dict[int, set[str]] = defaultdict(set)
    for cp in problems:
        number_category[cp.number].add(cp.category.identifier[0].upper())

    return " / ".join(f"{''.join(cat)}{n}" for n, cat in number_category.items())


@register.filter()
def timedelta_format(td: timedelta):
    total = td.total_seconds()
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)

    return ":".join([f"{int(x):02d}" for x in (hours, minutes, seconds)])


@register.filter()
def problem_solve_percentage(stats):
    per = stats["solved"] / stats["received"]
    per = round(per * 100, 1)
    return f"{per:0.1f}"
