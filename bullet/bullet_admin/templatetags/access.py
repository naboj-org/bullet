from bullet_admin.access import is_any_admin, is_branch_admin, is_country_admin
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


@register.simple_tag(takes_context=True, name="get_active_competition")
def get_active_competition_tag(context):
    request = context["request"]
    return get_active_competition(request)
