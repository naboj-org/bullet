from typing import TYPE_CHECKING

from bullet_admin.access import is_admin
from bullet_admin.utils import get_active_branch
from competitions.models.competitions import Competition
from django import template
from django.conf import settings

if TYPE_CHECKING:
    from web.models import PageBlock

register = template.Library()


@register.simple_tag(name="render_page_block", takes_context=True)
def page_block(context, block: "PageBlock"):
    ctx = {}
    if isinstance(block.data, dict):
        ctx = block.data

    request = context.request
    ctx["image_root"] = settings.MEDIA_URL + "files/" + request.BRANCH.identifier + "/"
    ctx["block"] = block

    user = context.request.user
    ctx["can_edit_block"] = False
    if user.is_authenticated:
        if context["competition"]:
            competition = context["competition"]
        else:
            competition = Competition.objects.get_current_competition(
                get_active_branch(request)
            )

        ctx["can_edit_block"] = is_admin(user, competition)  # type:ignore

    return block.block.render(context.request, ctx)
