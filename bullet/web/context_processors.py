from web.models import Menu


def menu_context(request):
    return {"menu": Menu.objects.order_by("order")}
