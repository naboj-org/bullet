from competitions.branches import Branches
from web.models import Menu


def menu_context(request):
    return {"menu": Menu.objects.order_by("order")}


def branch_context(request):
    return {"branch": request.BRANCH, "branches": Branches}
