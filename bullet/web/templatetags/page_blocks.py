from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from web.models import PageBlock

register = template.Library()


@register.simple_tag(name="render_page_block", takes_context=True)
def page_block(context, block: "PageBlock"):
    return block.block.render(context.request, block.data)
