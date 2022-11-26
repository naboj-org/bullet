from dataclasses import dataclass
from datetime import datetime, timedelta

from competitions.models import CategoryCompetition, Competition, Venue
from django.db.models import Q, QuerySet
from django_countries.fields import Country
from problems.models import ResultRow


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
    )


def get_venue_results(venue: Venue, time: timedelta = None) -> QuerySet[ResultRow]:
    return get_results(Q(team__venue=venue), time)


def get_country_results(
    country: str | Country, category: CategoryCompetition, time: timedelta = None
) -> QuerySet[ResultRow]:
    return get_results(
        Q(team__venue__category_competition=category, team__school__country=country),
        time,
    )


def get_category_results(
    category: CategoryCompetition, time: timedelta = None
) -> QuerySet[ResultRow]:
    return get_results(
        Q(team__venue__category_competition=category),
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
