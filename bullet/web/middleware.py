from django.conf import settings
from django.http import HttpResponseNotFound


class AdminDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.get_host()
        domain = domain.strip().removeprefix("www.").lower()
        if not domain.endswith(settings.PARENT_HOST):
            return HttpResponseNotFound("Invalid subdomain.")

        domain = domain.removesuffix(settings.PARENT_HOST).strip(".")

        request._subdomain_resolved = False

        if domain == "admin":
            request.urlconf = "web.urls_admin"
            request.BRANCH = None
            request._subdomain_resolved = True

        response = self.get_response(request)
        return response
