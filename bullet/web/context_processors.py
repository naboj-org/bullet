from competitions.branches import Branches
from web.models import Menu


def menu_context(request):
    if request.BRANCH is None:
        return {}
    return {
        "menu": Menu.objects.filter(
            branch=request.BRANCH,
            language=request.LANGUAGE_CODE,
            countries__contains=[request.COUNTRY_CODE.upper()],
        ).order_by("order")
    }


def branch_context(request):
    return {"branch": request.BRANCH, "branches": Branches}
