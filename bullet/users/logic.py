import string

from competitions.models import Category, Competition, Venue
from django.db.models import Count, F, Q, QuerySet
from django.utils import timezone
from users.models import Team


def venue_has_capacity(venue: Venue) -> bool:
    teams = Team.objects.competing().filter(venue=venue).count()
    return venue.capacity > teams


def school_has_capacity(team: Team) -> bool:
    venue: Venue = team.venue
    category: Category = venue.category
    competition: Competition = category.competition

    school_limit = category.max_teams_per_school
    if (
        competition.registration_second_round_start
        and competition.registration_second_round_start <= team.registered_at
    ):
        school_limit = category.max_teams_second_round

    teams_from_school = (
        Team.objects.competing()
        .filter(
            venue__category=category,
            school=team.school,
        )
        .count()
    )
    if school_limit == 0:
        return True
    return school_limit > teams_from_school


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


def _waiting_list(team_filter: Q, inner_filter: Q):
    return (
        Team.objects.filter(Q(is_waiting=True) & team_filter)
        .annotate(
            from_school=Count(
                "school__team",
                filter=(
                    Q(  # teams that were confirmed earlier than this team
                        school__team__confirmed_at__lte=F("confirmed_at"),
                        school__team__confirmed_at__isnull=False,
                    )
                    | Q(  # already competing teams
                        school__team__is_waiting=False,
                        school__team__confirmed_at__isnull=False,
                    )
                )
                & inner_filter,
            )
        )
        .order_by("from_school", "registered_at")
    )


def get_venue_waiting_list(venue: Venue) -> QuerySet[Team]:
    # We need all competition venues here to properly count registered
    # teams across all of them.
    all_venues = Venue.objects.filter(category=venue.category)
    return _waiting_list(Q(venue=venue), Q(school__team__venue__in=all_venues))


def get_venues_waiting_list(venues: QuerySet[Venue]) -> QuerySet[Team]:
    return _waiting_list(Q(venue__in=venues), Q(school__team__venue__in=venues))


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
