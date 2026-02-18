from typing import Optional

from competitions.models import Competition, Venue
from competitions.models.competitions import Category
from countries.utils import country_reverse
from django import template
from django.utils.translation import gettext as _
from django_countries.fields import Country

register = template.Library()


@register.inclusion_tag("problems/results/_selects.html", takes_context=True)
def results_selects(
    context,
    competition: Competition,
    category: Category,
    country: Optional[str] = None,
    venue: Optional[Venue] = None,
    competition_number: Optional[int] = None,
):
    request = context["request"]
    query_string = request.GET.urlencode()
    if query_string:
        query_string = "?" + query_string

    # Generate category options
    categories = Category.objects.filter(competition=competition).order_by("identifier")
    category_options = []
    for cat in categories:
        selected = cat.identifier == category.identifier
        link = reverse_category(
            competition_number,
            cat.identifier,
            country.lower() if country else None,
            query_string,
        )
        display_name = cat.identifier
        category_options.append((link, display_name, selected))

    # Generate country options
    countries_list = [
        Country(c)
        for c in Venue.objects.filter(category__competition=competition)
        .order_by("country")
        .distinct("country")
        .values_list("country", flat=True)
    ]

    country_options = []
    # International option
    international_link = reverse_category(
        competition_number, category.identifier, None, query_string
    )
    country_options.append((international_link, _("International"), country is None))

    for c in countries_list:
        assert c.code is not None
        if c.code != "__":  # Skip legacy OPEN category
            country_code = c.code.lower()
            selected = country and country.lower() == c.code.lower()
            link = reverse_category(
                competition_number,
                category.identifier,
                country_code,
                query_string,
            )
            country_options.append((link, c.name, selected))
        else:
            # Handle Open category
            country_code = c.code.lower()
            selected = country and country.lower() == c.code.lower()
            link = reverse_category(
                competition_number,
                category.identifier,
                country_code,
                query_string,
            )
            country_options.append((link, "Open", selected))

    # Generate venue options (only if country is selected)
    venue_options = []
    if country:
        venues = Venue.objects.filter(
            category__competition=competition,
            country=country.upper(),
            category=category,
        ).order_by("name")

        # "All venues" option
        all_venues_link = reverse_category(
            competition_number,
            category.identifier,
            country.lower() if country else None,
            query_string,
        )
        venue_options.append((all_venues_link, _("All venues"), venue is None))

        for v in venues:
            selected = venue and venue.shortcode.lower() == v.shortcode.lower()
            link = reverse_venue(competition_number, v.shortcode, query_string)
            venue_options.append((link, v.name, selected))

    return {
        "category_options": category_options,
        "country_options": country_options,
        "venue_options": venue_options,
    }


def reverse_category(competition_number, category, country, query_string):
    kwargs = {
        "category": category,
    }
    if country:
        kwargs["country"] = country

    urlname = "archive_results_category" if competition_number else "results_category"
    if competition_number:
        kwargs["competition_number"] = competition_number

    return country_reverse(urlname, kwargs=kwargs) + query_string


def reverse_venue(competition_number, venue, query_string):
    kwargs = {
        "venue": venue,
    }
    urlname = "archive_results_venue" if competition_number else "results_venue"
    if competition_number:
        kwargs["competition_number"] = competition_number

    return country_reverse(urlname, kwargs=kwargs) + query_string
