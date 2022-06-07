from django import template
from django.utils.safestring import mark_safe
from web.content_blocks import get_blocks_cache

register = template.Library()


@register.simple_tag(name="content_block", takes_context=True)
def content_block(context, ref):
    cache = get_blocks_cache()
    request = context.request

    keys = [
        (request.BRANCH.id, request.COUNTRY_CODE, request.LANGUAGE_CODE, ref),
        (request.BRANCH.id, None, request.LANGUAGE_CODE, ref),
        (None, request.COUNTRY_CODE, request.LANGUAGE_CODE, ref),
        (None, None, request.LANGUAGE_CODE, ref),
    ]

    for key in keys:
        if key in cache:
            return mark_safe(cache[key])

    return f"!!! MISSING CONTENT BLOCK {ref} !!!"
