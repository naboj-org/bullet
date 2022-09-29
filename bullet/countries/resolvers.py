import re
from copy import deepcopy

from countries.logic.country import get_country
from django.urls import URLResolver
from django.utils.translation import get_language


def country_patterns(*urls):
    return [
        CountryURLResolver(
            CountryLanguagePrefixPattern(),
            list(urls),
        )
    ]


class CountryURLResolver(URLResolver):
    """
    Django caches _reverse_dict by langauges, but we need
    to cache it by (country,language) pair.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._country_reverse_dict = {}
        self._country_namespace_dict = {}
        self._country_app_dict = {}

    def _populate(self):
        super()._populate()
        langauge_code = get_language()
        k = (get_country(), langauge_code)
        print(
            self._reverse_dict[langauge_code],
            type(self._reverse_dict[langauge_code]),
        )
        self._country_namespace_dict[k] = deepcopy(self._namespace_dict[langauge_code])
        self._country_app_dict[k] = deepcopy(self._app_dict[langauge_code])
        self._country_reverse_dict[k] = deepcopy(self._reverse_dict[langauge_code])

    @property
    def reverse_dict(self):
        k = (get_country(), get_language())
        if k not in self._country_reverse_dict:
            self._populate()
        return self._country_reverse_dict[k]

    @property
    def namespace_dict(self):
        k = (get_country(), get_language())
        if k not in self._country_namespace_dict:
            self._populate()
        return self._country_namespace_dict[k]

    @property
    def app_dict(self):
        k = (get_country(), get_language())
        if k not in self._country_app_dict:
            self._populate()
        return self._country_app_dict[k]


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
