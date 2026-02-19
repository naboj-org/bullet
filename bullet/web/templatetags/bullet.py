from competitions.branches import Branches
from countries.models import BranchCountry
from django import template

from web.models import Menu

register = template.Library()


@register.inclusion_tag("web/snippets/main_nav.html", takes_context=True)
def main_nav(context, primary=False):
    if "request" not in context:
        return context

    request = context["request"]
    if request.BRANCH is None or not hasattr(request, "COUNTRY_CODE"):
        return context

    if not hasattr(request, "_menu_cache"):
        request._menu_cache = Menu.objects.filter(
            branch=request.BRANCH,
            language=request.LANGUAGE_CODE,
            countries__contains=[request.COUNTRY_CODE.upper()],
            is_visible=True,
        ).order_by("order")

    context.update(
        {
            "menu": request._menu_cache,
            "primary": primary,
        }
    )
    return context


@register.inclusion_tag("web/snippets/branch_selector.html", takes_context=True)
def branch_selector(context):
    if "request" not in context:
        return {}
    request = context["request"]

    if request.BRANCH is None:
        return {}

    if not hasattr(request, "COUNTRY_CODE"):
        return {
            "branch": request.BRANCH,
            "branches": list(Branches),
        }

    return {
        "branch": request.BRANCH,
        "branches": [
            Branches[i.branch]
            for i in BranchCountry.objects.filter(
                country=request.COUNTRY_CODE.upper()
            ).order_by("branch")
        ],
    }
