from django.shortcuts import render
from django.views.generic import RedirectView


class AdminRedirectView(RedirectView):
    url = "/admin/"


def error_404_view(request, *args, **kwargs):
    response = render(request, "web/404.html")
    response.status_code = 404
    return response
