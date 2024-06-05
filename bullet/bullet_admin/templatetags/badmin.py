from bullet_admin.access import is_country_admin
from bullet_admin.utils import get_active_competition
from competitions.branches import Branch
from competitions.models import Competition
from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from users.models import User

from bullet.search import DumbPage

register = template.Library()


@register.inclusion_tag("bullet_admin/partials/sidebar_menu.html", takes_context=True)
def admin_sidebar(context):
    user: User = context.request.user
    branch: Branch = context.request.BRANCH
    competition: Competition = get_active_competition(context.request)

    menu_items = []

    branch_role = user.get_branch_role(branch)
    competition_role = user.get_competition_role(competition)
    any_admin = (
        branch_role.is_admin or competition_role.venues or competition_role.countries
    )

    country_admin = is_country_admin(user, competition)

    if any_admin:
        items = [("fa-users", "Teams", reverse("badmin:team_list"))]

        if not competition_role.is_operator:
            items.extend(
                [
                    ("fa-envelope", "Emails", reverse("badmin:email_list")),
                    ("fa-trash", "Deleted teams", reverse("badmin:recently_deleted")),
                ]
            )

        items.extend(
            [
                (
                    "fa-barcode",
                    "Problem scanning",
                    reverse("badmin:scanning_problems"),
                ),
                (
                    "fa-magnifying-glass",
                    "Review",
                    reverse("badmin:scanning_review"),
                ),
                ("fa-trophy", "Results", reverse("badmin:results")),
            ]
        )

        if country_admin:
            items.append(("fa-diamond", "Wildcards", reverse("badmin:wildcard_list")))

        menu_items.append(("Competition", items))

    if branch_role.is_translator:
        menu_items.append(
            (
                "Content",
                (
                    ("fa-file-text", "Pages", reverse("badmin:page_list")),
                    ("fa-cube", "Blocks", reverse("badmin:contentblock_list")),
                    ("fa-handshake", "Logos", reverse("badmin:logo_list")),
                    ("fa-bars", "Menu items", reverse("badmin:menu_list")),
                    ("fa-folder", "File browser", reverse("badmin:file_tree")),
                ),
            )
        )

    if branch_role.is_photographer or branch_role.is_admin:
        menu_items.append(
            (
                "Photos",
                (("fa-book-open", "Albums", reverse("badmin:album_list")),),
            )
        )

    if (
        branch_role.is_admin
        or competition_role.can_delegate
        or competition_role.countries
        or competition_role.venues
        and not competition_role.is_operator
    ):
        items = []

        if competition_role.can_delegate or branch_role.is_admin:
            items.append(("fa-users", "Users", reverse("badmin:user_list")))
        if user.is_superuser or branch_role.is_admin or competition_role.countries:
            items.append(("fa-building", "Schools", reverse("badmin:school_list")))
        if (
            user.is_superuser
            or branch_role.is_admin
            or competition_role.countries
            or competition_role.venues
        ):
            items.append(("fa-location-pin", "Venues", reverse("badmin:venue_list")))
            items.append(
                ("fa-file-text", "TeX Templates", reverse("badmin:tex_template_list"))
            )
        if branch_role.is_admin:
            items.append(
                ("fa-gear", "Edit Competition", reverse("badmin:competition_edit"))
            )
            items.append(
                ("fa-people-group", "Categories", reverse("badmin:category_list"))
            )
            items.append(
                ("fa-upload", "Import archive", reverse("badmin:archive_import"))
            )
        if branch_role.is_admin or competition_role.countries:
            items.append(
                (
                    "fa-upload",
                    "Upload problems",
                    reverse("badmin:archive_problem_upload"),
                )
            )
        if branch_role.is_admin:
            items.append(
                ("fa-book", "Problem settings", reverse("badmin:problems_generate"))
            )
            items.append(
                (
                    "fa-fast-forward",
                    "Move waiting lists",
                    reverse("badmin:competition_automove"),
                )
            )

        menu_items.append(
            (
                "Settings",
                items,
            )
        )

    context.update(
        {
            "menu_items": menu_items,
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
