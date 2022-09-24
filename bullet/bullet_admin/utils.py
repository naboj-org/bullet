from competitions.models import Competition
from django.http import HttpRequest


def get_active_competition(request: HttpRequest):
    if not hasattr(request, "_badmin_competition"):
        if "badmin_competition" not in request.session:
            request._badmin_competition = Competition.objects.get_current_competition(
                request.BRANCH
            )
        else:
            request._badmin_competition = (
                Competition.objects.filter(branch=request.BRANCH)
                .filter(id=request.session.get("badmin_competition"))
                .first()
            )

    return request._badmin_competition
