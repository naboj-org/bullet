import re
from re import Match, Pattern

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone, translation

from countries.logic import country
from countries.models import BranchCountry

country_language_re: Pattern[str] = re.compile(r"^/([a-z]{2})/([^/]+)/")
url_path_re: Pattern[str] = re.compile(r"^/[a-z]{2}/[^/]+/(.*)")


def country_language_from_request(
    request: HttpRequest,
) -> tuple[str, str] | tuple[None, None]:
    match: Match[str] | None = country_language_re.match(request.path_info)
    if not match:
        return None, None

    return match.groups()


class CountryLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def redirect_to_selector(self):
        return HttpResponseRedirect(reverse("country_selector"))

    def __call__(self, request: HttpRequest):
        c, lang = country_language_from_request(request)

        if not c or request._is_admin_domain:
            # Use default settings if not detected.
            timezone.activate(settings.TIME_ZONE)
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()
            return self.get_response(request)

        redirect = self.set_country_language(request, c, lang)
        if redirect:
            return redirect

        response = self.get_response(request)
        self.set_cookies(request, response)
        return response

    def get_url_part(self, request) -> str | None:
        match = url_path_re.match(request.path_info)
        if not match:
            return None

        return match.groups()[0]

    def set_country_language(
        self, request: HttpRequest, country_name, language
    ) -> HttpResponse | None:
        branch_country: BranchCountry = BranchCountry.objects.filter(
            branch=request.BRANCH, country=country_name.upper()
        ).first()

        if branch_country is None:
            return self.redirect_to_selector()

        if language not in branch_country.languages:
            url_part = self.get_url_part(request)
            if branch_country.primary_language and url_part:
                new_url = (
                    f"/{country_name}/{branch_country.primary_language}/{url_part}"
                )
                return HttpResponseRedirect(new_url)
            return self.redirect_to_selector()

        timezone.activate(branch_country.timezone)

        country.activate(country_name)
        request.COUNTRY_CODE = country_name

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

        return None

    def set_cookies(self, request, response):
        country = request.COUNTRY_CODE
        language = request.LANGUAGE_CODE

        if not country or not language:
            return

        ckie = request.COOKIES.get("bullet_country", "")
        expected = f"{country}|{language}"
        if ckie != expected:
            response.set_cookie(
                "bullet_country",
                expected,
                expires=365 * 24 * 60 * 60,
                samesite="Lax",
            )
