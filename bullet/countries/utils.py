from django.urls import reverse
from django.utils.translation import get_language

from countries.logic.country import get_country


def country_reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None):
    if kwargs is None:
        kwargs = {}
    kwargs["b_country"] = get_country()
    kwargs["b_language"] = get_language()

    return reverse(viewname, urlconf, args, kwargs, current_app)
