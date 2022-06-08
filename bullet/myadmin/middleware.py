from competitions.middleware import BranchMiddleware
from django.conf import settings
from django.urls import set_urlconf


class AdminDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ROOT_URLCONF = settings.ROOT_URLCONF
        self.BranchMiddleware = BranchMiddleware(get_response)

    def __call__(self, request):
        domain = request.get_host()
        domain = domain.strip().lstrip("www.").lower()
        if not domain.endswith(settings.PARENT_HOST):
            return None

        domain = domain.rstrip(settings.PARENT_HOST).strip(".")

        if domain == "admin":
            settings.ROOT_URLCONF = "myadmin.urls"
            set_urlconf(settings.ROOT_URLCONF)
            request.BRANCH = None
            response = self.get_response(request)
            return response
        else:
            settings.ROOT_URLCONF = self.ROOT_URLCONF
            set_urlconf(settings.ROOT_URLCONF)
            return self.BranchMiddleware(request)
