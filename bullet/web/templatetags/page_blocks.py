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
    ctx["image_root"] = (
        settings.MEDIA_URL + "files/" + context.request.BRANCH.identifier + "/"
    )
    return block.block.render(context.request, ctx)
