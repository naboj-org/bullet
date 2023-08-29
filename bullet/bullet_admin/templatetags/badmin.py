from bullet_admin.utils import get_active_competition
from competitions.branches import Branch
from django import template
from django.urls import reverse
from users.models import User

register = template.Library()


@register.inclusion_tag("bullet_admin/partials/sidebar_menu.html", takes_context=True)
def admin_sidebar(context):
    user: User = context.request.user
    branch: Branch = context.request.BRANCH

    menu_items = []

    branch_role = user.get_branch_role(branch)
    competition_role = user.get_competition_role(
        get_active_competition(context.request)
    )
    any_admin = (
        branch_role.is_admin or competition_role.venues or competition_role.countries
    )

    if any_admin:
        items = [("fa-users", "Teams", reverse("badmin:team_list"))]

        if not competition_role.is_operator:
            items.extend(
                [
                    ("fa-clock", "Waiting list", reverse("badmin:waiting_list")),
                    ("fa-envelope", "Emails", reverse("badmin:email_list")),
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
            ]
        )

        if not competition_role.is_operator:
            items.extend(
                [
                    ("fa-trophy", "Results", reverse("badmin:results")),
                ]
            )

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
                ),
            )
        )

    if (
        branch_role.is_admin
        or competition_role.can_delegate
        or competition_role.countries
        and not competition_role.is_operator
    ):
        items = []

        if competition_role.can_delegate or branch_role.is_admin:
            items.append(("fa-users", "Users", reverse("badmin:user_list")))
        if branch_role.is_admin or competition_role.countries:
            items.append(("fa-location-pin", "Venues", reverse("badmin:venue_list")))

        menu_items.append(
            (
                "Settings",
                items,
            )
        )

    if any_admin and not competition_role.is_operator:
        menu_items.append(
            (
                "Documents",
                (
                    (
                        "fa-certificate",
                        "Certificates",
                        reverse("badmin:docs_certificates"),
                    ),
                    (
                        "fa-list",
                        "Team lists",
                        reverse("badmin:docs_teamlists"),
                    ),
                ),
            )
        )

    context.update(
        {
            "menu_items": menu_items,
            "competition": get_active_competition(context.request),
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
    context["paginator"] = page.paginator
    context["pages"] = page.paginator.get_elided_page_range(page.number)
    context["page"] = page
    return context
