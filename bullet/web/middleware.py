from django.conf import settings
from django.http import HttpResponseNotFound
from django_minify_html.middleware import MinifyHtmlMiddleware


class AdminDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.get_host()
        domain = domain.strip().removeprefix("www.").lower()
        if not domain.endswith(settings.PARENT_HOST):
            return HttpResponseNotFound("Invalid subdomain.")

        domain = domain.removesuffix(settings.PARENT_HOST).strip(".")

        request._is_admin_domain = False

        if domain == "admin":
            request.urlconf = "web.urls_admin"
            request.BRANCH = None
            request._is_admin_domain = True

        response = self.get_response(request)
        return response


class BulletMinifyHtmlMiddleware(MinifyHtmlMiddleware):
    def should_minify(self, request, response) -> bool:
        is_admin = hasattr(request, "_is_admin_domain") and request._is_admin_domain
        return super().should_minify(request, response) and not is_admin
