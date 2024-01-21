import re
from re import Match, Pattern

from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone, translation

from countries.logic import country
from countries.logic.cache import get_country_cache
from countries.models import BranchCountry

country_language_re: Pattern[str] = re.compile(r"^/([a-z]{2})/([^/]+)/")


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

    def __call__(self, request: HttpRequest):
        c, lang = country_language_from_request(request)

        if c and not request._is_admin_domain:
            cache: dict[int, dict[str, list[tuple[str, bool]]]] = get_country_cache()
            if request.BRANCH is not None and (
                c not in cache[request.BRANCH.id]
                or (
                    (lang, True) not in cache[request.BRANCH.id][c]
                    and (lang, False) not in cache[request.BRANCH.id][c]
                )
            ):
                return HttpResponseRedirect(reverse("country_selector"))

            country.activate(c)
            request.COUNTRY_CODE = c

            branch_country = BranchCountry.objects.get(
                branch=request.BRANCH, country=c.upper()
            )
            timezone.activate(branch_country.timezone)

            translation.activate(lang)
            request.LANGUAGE_CODE = translation.get_language()
        else:
            # Use default settings if not detected.
            timezone.activate(settings.TIME_ZONE)
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)

        if c and not request._is_admin_domain:
            ckie = request.COOKIES.get("bullet_country", "")
            expected = f"{c}|{lang}"
            if ckie != expected:
                response.set_cookie(
                    "bullet_country",
                    expected,
                    expires=365 * 24 * 60 * 60,
                    samesite="Lax",
                )

        return response
