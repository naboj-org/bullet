from typing import TYPE_CHECKING

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
    is_translator = user.get_branch_role(request.BRANCH).is_translator
    if user.is_authenticated and (user.is_superuser or is_translator):
        ctx["can_edit_block"] = True

    return block.block.render(context.request, ctx)
