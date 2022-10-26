from competitions.branches import Branch
from competitions.models import Competition
from countries.models import BranchCountry
from django.utils.translation import get_language_info
from django_countries.fields import Country
from users.models import User


def get_country_choices(competition: Competition, user: User = None, allow_empty=False):
    countries = [
        Country(c)
        for c in BranchCountry.objects.filter(branch=competition.branch).values_list(
            "country", flat=True
        )
    ]

    choices = [(c.code, c.name) for c in countries]
    choices.sort(key=lambda x: x[1])

    if not user.get_branch_role(competition.branch).is_admin:
        crole = user.get_competition_role(competition)
        choices = list(filter(lambda x: x[0] in crole.countries, choices))

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
