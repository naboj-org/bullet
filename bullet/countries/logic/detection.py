from __future__ import annotations

from countries.logic.cache import get_country_cache
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.http import HttpRequest
from django.utils.translation import get_language_info
from django.utils.translation.trans_real import parse_accept_lang_header
from geoip2.errors import AddressNotFoundError


def _country_from_ip(request: HttpRequest) -> str | None:
    x_forwarded_for: str = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        ip: str = x_forwarded_for.split(",")[-1].strip()
    else:
        ip: str = request.META.get("REMOTE_ADDR", "")
    try:
        g: GeoIP2 = GeoIP2()
        return g.country_code(ip).lower()
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
    lang: str | None = None
    langs: list[str] = _language_from_header(request)
    if "bullet_country" in request.COOKIES:
        country, lang = request.COOKIES["bullet_country"].split("|", 1)

    if country is None:
        country = _country_from_ip(request)

    if country is None or country not in cache[request.BRANCH.id]:
        return None

    if lang:
        langs.insert(0, lang)

    for language in langs:
        if language in cache[request.BRANCH.id][country]:
            return country, language

    return country, cache[request.BRANCH.id][country][0]
