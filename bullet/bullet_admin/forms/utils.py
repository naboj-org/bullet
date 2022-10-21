from competitions.branches import Branch
from countries.models import BranchCountry
from django.utils.translation import get_language_info
from django_countries.fields import Country


def get_country_choices(branch: Branch, allow_empty=False):
    countries = [
        Country(c)
        for c in BranchCountry.objects.filter(branch=branch).values_list(
            "country", flat=True
        )
    ]

    choices = [(c.code, c.name) for c in countries]
    choices.sort(key=lambda x: x[1])

    if allow_empty:
        choices.insert(0, ("", "--------"))

    return choices


def get_language_choices(branch: Branch, allow_empty=False):
    languages = set()
    language_lists = BranchCountry.objects.filter(branch=branch).values_list(
        "languages", flat=True
    )
    for langs in language_lists:
        languages.update(set(langs))

    choices = [(lang, get_language_info(lang)["name_translated"]) for lang in languages]
    choices.sort(key=lambda x: x[1])

    if allow_empty:
        choices.insert(0, ("", "--------"))

    return choices
