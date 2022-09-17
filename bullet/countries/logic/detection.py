from __future__ import annotations

from countries.logic.cache import get_country_cache
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.http import HttpRequest
from django.utils.translation import get_language_info
from django.utils.translation.trans_real import parse_accept_lang_header
from geoip2.errors import AddressNotFoundError


def _ip_from_request(request: HttpRequest) -> str:
    if "HTTP_X_FORWARDED_FOR" in request.META:
        return request.META["HTTP_X_FORWARDED_FOR"].split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")


def _country_from_ip(request: HttpRequest) -> str | None:
    try:
        g: GeoIP2 = GeoIP2()
        return g.country_code(_ip_from_request(request)).lower()
    except GeoIP2Exception:
        return None
    except AddressNotFoundError:
        return None


def _language_from_header(request: HttpRequest) -> list[str]:
    accept: str = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    ret: list[str] = []

    for accept_lang, unused in parse_accept_lang_header(accept):
        try:
            ret.append(get_language_info(accept_lang)["code"])
        except KeyError:
            continue
    return ret


def get_country_language_from_request(request: HttpRequest) -> tuple[str, str] | None:
    cache: dict[int, dict[str, list[str]]] = get_country_cache()
    country: str | None = None
    langs: list[str] = _language_from_header(request)

    # Check existing cookies
    cookie = request.COOKIES.get("bullet_country", "")
    if "|" in cookie:
        country, lang = request.COOKIES["bullet_country"].split("|", 1)
        langs.insert(0, lang)

    # If cookie was absent, try getting country from IP
    if country is None:
        country = _country_from_ip(request)

    # We failed to detect country or it's not available for this branch
    if not country or country not in cache[request.BRANCH.id]:
        return None

    # We check all languages from Accept-Language header and select the first available
    for language in langs:
        if language in cache[request.BRANCH.id][country]:
            return country, language

    # If everything failed, we fallback to country's first language
    return country, cache[request.BRANCH.id][country][0]
