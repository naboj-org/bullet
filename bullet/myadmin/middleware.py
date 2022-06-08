from django.conf import settings
from django.urls import set_urlconf


class AdminDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ROOT_URLCONF = settings.ROOT_URLCONF

    def __call__(self, request):
        domain = request.get_host()
        domain = domain.strip().lstrip("www.").lower()
        if not domain.endswith(settings.PARENT_HOST):
            return None

        domain = domain.rstrip(settings.PARENT_HOST).strip(".")

        settings.ROOT_URLCONF = self.ROOT_URLCONF
        request._subdomain_resolved = False

        if domain == "admin":
            settings.ROOT_URLCONF = "myadmin.urls"
            request.BRANCH = None
            request._subdomain_resolved = True

        set_urlconf(settings.ROOT_URLCONF)
        response = self.get_response(request)
        return response
