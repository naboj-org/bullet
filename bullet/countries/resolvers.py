import re

from countries.logic.country import get_country
from django.urls import URLResolver
from django.utils.translation import get_language


def country_patterns(*urls):
    return [
        URLResolver(
            CountryLanguagePrefixPattern(),
            list(urls),
        )
    ]


class CountryLanguagePrefixPattern:
    """
    Based on django.urls.resolvers.LocalePrefixPattern
    """

    def __init__(self):
        self.converters = {}

    @property
    def regex(self):
        # This is only used by reverse() and cached in _reverse_dict.
        return re.compile(self.prefix)

    @property
    def prefix(self):
        country_code = get_country()
        language_code = get_language()

        if not country_code or not language_code:
            return "-/-/"

        return f"{country_code}/{language_code}/"

    def match(self, path):
        prefix = self.prefix
        if prefix == "-/-/":
            return None

        if path.startswith(prefix):
            return path[len(prefix) :], (), {}
        return None

    def check(self):
        return []

    def describe(self):
        return "'{}'".format(self)

    def __str__(self):
        return self.prefix
