from typing import Callable

from bullet_admin.access import (
    CompetitionPermissionCallable,
    VenuePermissionCallable,
    is_admin,
    is_admin_in,
    is_branch_admin,
    is_branch_admin_in,
    is_country_admin,
    is_country_admin_in,
    is_operator,
    is_operator_in,
)
from bullet_admin.utils import get_active_competition
from competitions.models.venues import Venue
from django import template
from django.http import HttpRequest
from users.models.organizers import User

register = template.Library()


def competition_check(perm: CompetitionPermissionCallable) -> Callable:
    def fn(context):
        request: HttpRequest = context["request"]

        user = request.user
        assert isinstance(user, User)
        competition = get_active_competition(request)

        return perm(user, competition)

    return fn


def venue_check(perm: VenuePermissionCallable) -> Callable:
    def fn(context, venue: Venue | None = None):
        request: HttpRequest = context["request"]

        if not venue:
            if "venue" in context:
                venue = context["venue"]
            else:
                raise ValueError(f"{perm.__name__} called without venue")

        user = request.user
        assert isinstance(user, User)

        return perm(user, venue)  # type:ignore

    return fn


register.simple_tag(
    competition_check(is_branch_admin), takes_context=True, name="is_branch_admin"
)
register.simple_tag(
    competition_check(is_country_admin), takes_context=True, name="is_country_admin"
)
register.simple_tag(competition_check(is_admin), takes_context=True, name="is_admin")
register.simple_tag(
    competition_check(is_operator), takes_context=True, name="is_operator"
)

register.simple_tag(
    venue_check(is_branch_admin_in), takes_context=True, name="is_branch_admin_in"
)
register.simple_tag(
    venue_check(is_country_admin_in), takes_context=True, name="is_country_admin_in"
)
register.simple_tag(venue_check(is_admin_in), takes_context=True, name="is_admin_in")
register.simple_tag(
    venue_check(is_operator_in), takes_context=True, name="is_operator_in"
)


@register.simple_tag(takes_context=True, name="get_active_competition")
def get_active_competition_tag(context):
    request = context["request"]
    return get_active_competition(request)
