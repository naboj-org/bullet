from countries.logic.cache import get_country_cache
from django.http import HttpRequest


def get_country_language_from_request(request: HttpRequest) -> tuple[str, str] | None:
    c = _detect(request)
    if c is None:
        return None

    c, lang = c

    if (request.BRANCH.id, c, lang) not in get_country_cache():
        return None

    return c, lang


def _detect(request: HttpRequest) -> tuple[str, str] | None:
    if "bullet_country" in request.COOKIES:
        return request.COOKIES["bullet_country"].split("|", 1)

    # todo: GeoIP detection
    return None
