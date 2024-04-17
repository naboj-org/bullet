from bullet_admin.access import (
    can_access_venue,
    is_any_admin,
    is_branch_admin,
    is_country_admin,
    is_country_admin_in,
)
from bullet_admin.utils import get_active_competition
from django import template

register = template.Library()


@register.simple_tag(takes_context=True, name="is_any_admin")
def is_any_admin_tag(context):
    request = context["request"]
    return is_any_admin(request.user, get_active_competition(request))


@register.simple_tag(takes_context=True, name="is_country_admin")
def is_country_admin_tag(context):
    request = context["request"]
    return is_country_admin(request.user, get_active_competition(request))


@register.simple_tag(takes_context=True, name="is_country_admin_in")
def is_country_admin_in_tag(context, country):
    request = context["request"]
    return is_country_admin_in(request.user, get_active_competition(request), country)


@register.simple_tag(takes_context=True, name="is_venue_admin")
def is_venue_admin_tag(context, venue):
    request = context["request"]
    return can_access_venue(request.user, venue)


@register.simple_tag(takes_context=True, name="is_branch_admin")
def is_branch_admin_tag(context):
    request = context["request"]
    return is_branch_admin(request.user, request.BRANCH)


@register.simple_tag(takes_context=True, name="is_any_operator")
def is_any_operator_tag(context):
    request = context["request"]
    return is_any_admin(
        request.user, get_active_competition(request), allow_operator=True
    )


@register.simple_tag(takes_context=True, name="is_country_operator")
def is_country_operator_tag(context):
    request = context["request"]
    return is_country_admin(
        request.user, get_active_competition(request), allow_operator=True
    )


@register.simple_tag(takes_context=True, name="is_country_operator_in")
def is_country_operator_in_tag(context, country):
    request = context["request"]
    return is_country_admin_in(
        request.user, get_active_competition(request), country, allow_operator=True
    )


@register.simple_tag(takes_context=True, name="get_active_competition")
def get_active_competition_tag(context):
    request = context["request"]
    return get_active_competition(request)
