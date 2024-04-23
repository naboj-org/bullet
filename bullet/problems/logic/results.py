from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from competitions.models import Category, Competition, Venue
from django.db import transaction
from django.db.models import Q, QuerySet
from django_countries.fields import Country
from django_rq import job
from users.models import Team

from problems.models import CategoryProblem, ResultRow, SolvedProblem


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


@job
@transaction.atomic
def squash_results(competition: Competition | int):
    if isinstance(competition, int):
        competition = Competition.objects.get(id=competition)

    ResultRow.objects.filter(team__venue__category__competition=competition).delete()

    teams = Team.objects.filter(venue__category__competition=competition)
    for team in teams:
        problems = (
            SolvedProblem.objects.filter(team=team)
            .values_list("problem")
            .order_by("-competition_time")
        )
        last_problem = (
            SolvedProblem.objects.filter(team=team)
            .order_by("-competition_time")
            .first()
        )
        solved_problems = set(
            CategoryProblem.objects.filter(
                problem__in=problems, category=team.venue.category
            ).values_list("number", flat=True)
        )

        if not last_problem:
            continue

        result_row = ResultRow()
        result_row.team = team
        result_row.solved_count = len(solved_problems)

        solved_bin = 0
        for p in solved_problems:
            solved_bin |= 1 << (p - 1)
        result_row.solved_problems = solved_bin.to_bytes(16, "big")

        result_row.competition_time = last_problem.competition_time
        result_row.save()


def _save_ranks(results: Iterable[ResultRow], where: str):
    rank = 1
    for row in results:
        team = row.team
        setattr(team, where, rank)
        team._change_reason = f"storing {where}"
        team.save(send_to_search=False)
        rank += 1


@job
@transaction.atomic
def save_venue_ranks(venue: Venue | int):
    if isinstance(venue, int):
        venue = Venue.objects.get(id=venue)

    Team.objects.filter(venue=venue).update(rank_venue=None)

    results = get_venue_results(venue)
    _save_ranks(results, "rank_venue")


@job
@transaction.atomic
def save_country_ranks(category: Category | int, country: str):
    if isinstance(category, int):
        category = Category.objects.get(id=category)

    Team.objects.filter(venue__category=category, venue__country=country).update(
        rank_country=None
    )

    results = get_country_results(country, category)
    _save_ranks(results, "rank_country")


@job
@transaction.atomic
def save_international_ranks(category: Category | int):
    if isinstance(category, int):
        category = Category.objects.get(id=category)

    Team.objects.filter(venue__category=category).update(rank_international=None)

    results = get_category_results(category)
    _save_ranks(results, "rank_international")


@job
def save_all_ranks(competition: Competition | int):
    if isinstance(competition, int):
        competition = Competition.objects.get(id=competition)

    venues = Venue.objects.filter(category__competition=competition)
    for venue in venues:
        save_venue_ranks(venue)

    categories = Category.objects.filter(competition=competition)
    countries = (
        venues.order_by("country").distinct("country").values_list("country", flat=True)
    )
    for country in countries:
        for category in categories:
            save_country_ranks(category, country)

    for category in categories:
        save_international_ranks(category)
