import string
from collections import defaultdict
from typing import Iterable, Protocol, Sequence, Union

from competitions.models import Category, Competition, Venue, Wildcard
from django.db.models import Count, QuerySet
from django.utils import timezone
from education.models import School

from users.models import Team


def venue_has_capacity(venue: Venue) -> bool:
    teams = Team.objects.competing().filter(venue=venue).count()
    return venue.capacity > teams


def get_team_count_per_category(
    competition: Competition, school: School
) -> dict[int, int]:
    """
    Returns a mapping between category ID and number of teams from a given school.
    """
    counts = (
        Team.objects.competing()
        .filter(venue__category__competition=competition, school=school)
        .values("venue__category")
        .annotate(count=Count("*"))
    )
    output = {item["venue__category"]: item["count"] for item in counts}
    return defaultdict(lambda: 0, output)


def wildcard_count_per_category(
    competition: Competition, school: School
) -> dict[int | None, int]:
    """
    Returns a mapping between category ID and number of wildcards for a given school.
    """
    counts = (
        Wildcard.objects.filter(competition=competition, school=school)
        .values("category")
        .annotate(count=Count("*"))
    )
    output = {item["category"]: item["count"] for item in counts}
    return defaultdict(lambda: 0, output)


def school_has_capacity(team: Team) -> bool:
    venue: Venue = team.venue
    category: Category = venue.category
    competition: Competition = category.competition

    category_team_limit = category.max_teams_per_school_at(team.registered_at)
    if category_team_limit == 0:
        return True

    wildcard_counts = wildcard_count_per_category(competition, team.school)
    team_counts = get_team_count_per_category(competition, team.school)

    teams_in_this_category = team_counts[category.id]
    wildcards_in_this_category = wildcard_counts[category.id]
    total_allowed_teams = category_team_limit + wildcards_in_this_category

    if teams_in_this_category < total_allowed_teams:
        return True

    universal_wildcards = wildcard_counts[None]
    used_universal_wildcards = 0
    for cat in competition.category_set.all():
        used_universal_wildcards += max(
            0,
            team_counts[cat.id]
            - cat.max_teams_per_school_at(team.registered_at)
            - wildcard_counts[cat.id],
        )

    return universal_wildcards - used_universal_wildcards > 0


def add_team_to_competition(team: Team):
    venue: Venue = team.venue

    # If registration closed -> waiting list
    if timezone.now() > venue.category.competition.registration_end:
        team.to_waitlist()
        return

    # If venue is over capacity -> waiting list
    if not venue_has_capacity(venue):
        team.to_waitlist()
        return

    # If school has no more available teams -> waiting list
    if team.school_id and not school_has_capacity(team):
        team.to_waitlist()
        return

    team.to_competition()


class HasWaitingListMeta(Protocol):
    from_school: int
    from_school_corrected: int
    wildcards: int


WaitingListTeam = Union[Team, HasWaitingListMeta]


def _waiting_list(
    competition: Competition, venues: Iterable[Venue]
) -> Sequence[WaitingListTeam]:
    waiting_teams = (
        Team.objects.filter(is_waiting=True, venue__category__competition=competition)
        .order_by("registered_at")
        .select_related("school", "venue")
        .prefetch_related("contestants", "contestants__grade")
    )
    related_schools = waiting_teams.values("school")

    teams_from_school = (
        Team.objects.competing()
        .filter(venue__category__competition=competition, school__in=related_schools)
        .values("school", "venue__category")
        .annotate(count=Count("*"))
    )
    teams_from_school = defaultdict(
        lambda: 0,
        {(x["school"], x["venue__category"]): x["count"] for x in teams_from_school},
    )

    wildcards_in_school = (
        Wildcard.objects.filter(
            school__in=related_schools, category__isnull=False, competition=competition
        )
        .values("school", "category")
        .annotate(count=Count("*"))
    )
    wildcards_in_school = defaultdict(
        lambda: 0,
        {(x["school"], x["category"]): x["count"] for x in wildcards_in_school},
    )

    our_teams = []

    for team in waiting_teams:
        school = team.school_id
        category = team.venue.category_id

        teams_from_school[school, category] += 1
        team.from_school = teams_from_school[school, category]
        team.wildcards = wildcards_in_school[school, category]
        team.from_school_corrected = team.from_school - team.wildcards

        if team.venue in venues:
            our_teams.append(team)

    return sorted(our_teams, key=lambda t: (t.from_school_corrected, t.registered_at))


def get_venue_waiting_list(venue: Venue) -> Sequence[WaitingListTeam]:
    # We need all competition venues here to properly count registered
    # teams across all of them.
    return _waiting_list(venue.category.competition, [venue])


def get_venues_waiting_list(
    competition: Competition, venues: QuerySet[Venue]
) -> Sequence[WaitingListTeam]:
    return _waiting_list(competition, venues.all())


def get_school_symbol(n: int) -> str:
    symbol = []
    while n > 0:
        rem = n % 26

        if rem == 0:
            symbol.append("Z")
            n = (n // 26) - 1
        else:
            symbol.append(string.ascii_uppercase[rem - 1])
            n //= 26

    return "".join(symbol[::-1])
