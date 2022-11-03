from competitions.models import Competition, Venue
from django.http import HttpRequest
from users.models import User


def get_active_competition(request: HttpRequest):
    if not hasattr(request, "_badmin_competition"):
        if "badmin_competition" not in request.session:
            request._badmin_competition = Competition.objects.get_current_competition(
                request.BRANCH
            )
        else:
            request._badmin_competition = Competition.objects.filter(
                branch=request.BRANCH, id=request.session.get("badmin_competition")
            ).first()

    return request._badmin_competition


def can_access_venue(request: HttpRequest, venue: Venue) -> bool:
    brole = request.user.get_branch_role(request.BRANCH)
    if (
        brole.is_admin
        and venue.category_competition.competition.branch == request.BRANCH
    ):
        return True

    competition = get_active_competition(request)
    if not competition or venue.category_competition.competition != competition:
        return False
    crole = request.user.get_competition_role(competition)
    if crole.venues:
        return venue in crole.venues
    if crole.countries:
        return venue.country in crole.countries

    return False


def is_admin(user: User, competition: Competition):
    if not user.is_authenticated:
        return False

    brole = user.get_branch_role(competition.branch)
    if brole.is_admin:
        return True

    crole = user.get_competition_role(competition)
    return (crole.venues or crole.countries) and not crole.is_operator
