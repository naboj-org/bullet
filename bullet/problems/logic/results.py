from dataclasses import dataclass
from datetime import datetime, timedelta

from competitions.models import Category, Competition, Venue
from django.db import transaction
from django.db.models import Q, QuerySet
from django_countries.fields import Country
from problems.models import CategoryProblem, ResultRow, SolvedProblem
from users.models import Team


def get_results(
    team_filter: Q,
    time: timedelta = None,
) -> QuerySet[ResultRow]:
    rows = ResultRow.objects.filter(team__is_disqualified=False)

    if team_filter:
        rows = rows.filter(team_filter)
    if time:
        rows = rows.filter(competition_time__lte=time)

    rows = rows.order_by("team_id", "-competition_time").distinct("team_id")

    return (
        ResultRow.objects.filter(id__in=rows)
        .order_by("-solved_count", "-solved_problems", "competition_time")
        .select_related("team", "team__school")
        .prefetch_related("team__contestants", "team__contestants__grade")
    )


def get_venue_results(venue: Venue, time: timedelta = None) -> QuerySet[ResultRow]:
    return get_results(Q(team__venue=venue), time)


def get_country_results(
    country: str | Country, category: Category, time: timedelta = None
) -> QuerySet[ResultRow]:
    return get_results(
        Q(team__venue__category=category, team__school__country=country),
        time,
    )


def get_category_results(
    category: Category, time: timedelta = None
) -> QuerySet[ResultRow]:
    return get_results(
        Q(team__venue__category=category),
        time,
    )


@dataclass
class ResultsTime:
    time: timedelta | None
    has_started: bool = False
    is_frozen: bool = False
    is_final: bool = False


def results_time(
    competition: Competition,
    realtime: datetime,
    start_time: datetime = None,
    is_admin: bool = False,
) -> ResultsTime:
    if not start_time:
        start_time = competition.competition_start

    if start_time > realtime:
        return ResultsTime(timedelta(seconds=-1))

    competition_end = start_time + competition.competition_duration
    if competition_end <= realtime and competition.results_public:
        return ResultsTime(None, True, False, True)

    if competition_end - competition.results_freeze <= realtime and not is_admin:
        return ResultsTime(
            competition.competition_duration - competition.results_freeze,
            True,
            True,
            False,
        )
    return ResultsTime(realtime - start_time, True, False, False)


def _set_solved_problems(rr: ResultRow):
    problems = (
        SolvedProblem.objects.select_for_update()
        .filter(team=rr.team, competition_time__lte=rr.competition_time)
        .values_list("problem")
    )
    solved_problems = set(
        CategoryProblem.objects.filter(
            problem__in=problems, category=rr.team.venue.category
        ).values_list("number", flat=True)
    )

    rr.solved_count = len(solved_problems)

    solved_bin = 0
    for p in solved_problems:
        solved_bin |= 1 << (p - 1)

    rr.solved_problems = solved_bin.to_bytes(16, "big")


@transaction.atomic
def add_result_row(team: Team, competition_time: timedelta):
    result_row = ResultRow()
    result_row.team = team
    result_row.competition_time = competition_time
    _set_solved_problems(result_row)
    result_row.save()


@transaction.atomic
def fix_result_row(result_row: ResultRow):
    _set_solved_problems(result_row)
    result_row.save()
