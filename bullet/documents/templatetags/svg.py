import textwrap

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def svg_wordwrap(text: str, args: str):
    chars, x = map(int, args.split(","))
    lines = textwrap.wrap(text, chars)
    svg = []
    for i, line in enumerate(lines):
        if i == 0:
            svg.append(f'<tspan x="{x}">{line}</tspan>')
        else:
            svg.append(f'<tspan x="{x}" dy="1.2em">{line}</tspan>')
    return mark_safe("".join(svg))
