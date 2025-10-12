from bullet.search import DumbPage
from bullet_admin.sidebar import get_sidebar
from bullet_admin.utils import get_active_competition
from competitions.models import Competition
from django import template
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe
from users.models import User

register = template.Library()


@register.inclusion_tag("bullet_admin/partials/sidebar_menu.html", takes_context=True)
def admin_sidebar(context):
    user: User = context.request.user
    competition: Competition = get_active_competition(context.request)
    context.update(
        {
            "menu_items": get_sidebar(user, competition),
            "competition": get_active_competition(context.request),
            "is_staging": settings.PARENT_HOST != "naboj.org",
        }
    )
    return context


@register.inclusion_tag("bullet_admin/form.html")
def admin_form(form):
    return {"form": form}


@register.inclusion_tag("bullet_admin/new_form.html")
def admin_form2(form):
    return {"form": form}


@register.inclusion_tag("bullet_admin/paginator.html", takes_context=True)
def admin_paginator(context, page):
    if not isinstance(page, DumbPage):
        context["ellipsis"] = page.paginator.ELLIPSIS
        context["pages"] = page.paginator.get_elided_page_range(page.number)
    context["page"] = page
    return context


@register.simple_tag()
def percent(value, max_value):
    if max_value == 0:
        return "0"
    return f"{float(value) / float(max_value) * 100:0.2f}"


@register.filter()
def highlight_barcode(barcode):
    barcode = escape(barcode)
    if len(barcode) != 11:
        return barcode
    return mark_safe(
        f'{barcode[0:4]}<b class="text-base">{barcode[4:8]}</b>{barcode[8:]}'
    )
