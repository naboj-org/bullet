from django import template

from web import content_blocks

register = template.Library()


@register.simple_tag(name="load_blocks", takes_context=True)
def load_blocks(context, *groups):
    content_blocks.load_blocks(context.request, *groups)
    return ""


@register.simple_tag(name="content_block", takes_context=True)
def content_block(context, combined_ref, allow_empty=False):
    return content_blocks.get_block(context.request, combined_ref, allow_empty)
