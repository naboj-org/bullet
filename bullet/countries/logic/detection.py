from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.utils.translation import get_language_info
from django.utils.translation.trans_real import parse_accept_lang_header
from geoip2.errors import AddressNotFoundError
from ipware import get_client_ip

from countries.logic.cache import get_country_cache


def _country_from_ip(request: "HttpRequest") -> str | None:
    try:
        g: GeoIP2 = GeoIP2()
        ip, _ = get_client_ip(request)
        if not ip:
            return None
        country_code: str = g.country_code(ip)
        if not country_code:
            return None
        return country_code.lower()
    except GeoIP2Exception:
        return None
    except AddressNotFoundError:
        return None


def _language_from_header(request: "HttpRequest") -> list[str]:
    accept: str = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    ret: list[str] = []

    for accept_lang, unused in parse_accept_lang_header(accept):
        try:
            ret.append(get_language_info(accept_lang)["code"])
        except KeyError:
            continue
    return ret


def get_country_language_from_request(request: "HttpRequest") -> tuple[str, str] | None:
    cache: dict[int, dict[str, list[tuple[str, bool]]]] = get_country_cache()
    country: str | None = None
    langs: list[str] = _language_from_header(request)

    # Check existing cookies
    cookie: str = request.COOKIES.get("bullet_country", "")
    if "|" in cookie:
        country, lang = request.COOKIES["bullet_country"].split("|", 1)
        langs.insert(0, lang)

    # If cookie was absent, try getting country from IP
    if country is None:
        country = _country_from_ip(request)

    # We failed to detect country, or it's not available for this branch
    if not country or country not in cache[request.BRANCH.id]:
        return None

    # We check all languages from Accept-Language header and select the first available
    for language in langs:
        if (language, True) in cache[request.BRANCH.id][country]:
            return country, language

    # We return first public language for this country
    for language, public in cache[request.BRANCH.id][country]:
        if public:
            return country, language

    # If everything failed, we fall back to country selector
    return None
