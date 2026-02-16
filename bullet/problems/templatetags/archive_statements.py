from datetime import timedelta

from django import template

register = template.Library()


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
