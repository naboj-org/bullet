from competitions.branches import Branches
from countries.models import BranchCountry
from web.models import Menu


def menu_context(request):
    if request.BRANCH is None or not hasattr(request, "COUNTRY_CODE"):
        return {}
    return {
        "menu": Menu.objects.filter(
            branch=request.BRANCH,
            language=request.LANGUAGE_CODE,
            countries__contains=[request.COUNTRY_CODE.upper()],
        ).order_by("order")
    }


def branch_context(request):
    if request.BRANCH is None or not hasattr(request, "COUNTRY_CODE"):
        return {
            "branch": request.BRANCH,
        }
    return {
        "branch": request.BRANCH,
        "branches": [
            Branches[i.branch]
            for i in BranchCountry.objects.filter(country=request.COUNTRY_CODE.upper())
        ],
    }
