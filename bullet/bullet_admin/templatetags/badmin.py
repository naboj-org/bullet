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
    if branch_role.is_admin or competition_role.venue or competition_role.country:
        menu_items.append(
            (
                "Competition",
                (
                    ("fa-users", "Teams", reverse("badmin:team_list")),
                    ("fa-clock", "Waiting list", reverse("badmin:waiting_list")),
                ),
            ),
        )

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

    if branch_role.is_admin or competition_role.can_delegate:
        menu_items.append(
            (
                "Access",
                (("fa-users", "Users", reverse("badmin:user_list")),),
            )
        )

    context.update(
        {
            "menu_items": menu_items,
            "competition": get_active_competition(context.request),
        }
    )
    return context
