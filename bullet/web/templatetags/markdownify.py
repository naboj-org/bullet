from competitions.models import Competition
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from markdown import markdown

register = template.Library()


# Given a relative path that has a {branch} template within, substitutes a branch string
# into the path and resolves into the full URI
@register.simple_tag(name="branch_static", takes_context=True)
def do_branch_static(context, path):
    if "branch" in context and isinstance(context["branch"], Competition.Branch):
        return static(path.format(branch=context["branch"].label.lower()))


@register.filter
def markdownify(content):
    return mark_safe(
        markdown(
            content,
            extensions=[
                "abbr",
                "admonition",
                "attr_list",
                "footnotes",
                "md_in_html",
                "sane_lists",
                "tables",
                "smarty",
            ],
        )
    )
