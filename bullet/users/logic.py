from competitions.models import CategoryCompetition, Competition, Venue
from users.models import Team


def venue_has_capacity(venue: Venue) -> bool:
    teams = Team.objects.competing().filter(venue=venue).count()
    return venue.capacity > teams


def school_has_capacity(team: Team) -> bool:
    venue: Venue = team.venue
    category: CategoryCompetition = venue.category_competition
    competition: Competition = category.competition

    school_limit = category.max_teams_per_school
    if (
        competition.registration_second_round_start
        and competition.registration_second_round_start <= team.registered_at
    ):
        school_limit = category.max_teams_second_round

    teams_from_school = (
        Team.objects.competing().filter(venue=venue, school=team.school).count()
    )
    if school_limit == 0:
        return True
    return school_limit > teams_from_school


def add_team_to_competition(team: Team):
    venue: Venue = team.venue

    # If venue is over capacity -> waiting list
    if not venue_has_capacity(venue):
        team.to_waitlist()
        return

    # If school has no more available teams -> waiting list
    if team.school_id and not school_has_capacity(team):
        team.to_waitlist()
        return

    team.to_competition()
