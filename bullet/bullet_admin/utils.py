from competitions.models import Competition, Venue
from django.http import HttpRequest


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
    if brole.is_admin:
        return True

    competition = get_active_competition(request)
    if not competition:
        return False
    crole = request.user.get_competition_role(competition)
    if crole.venue:
        return crole.venue == venue
    if crole.country:
        return crole.country == venue.country

    return False
