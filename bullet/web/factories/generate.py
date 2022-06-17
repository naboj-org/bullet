from competitions.branches import Branch
from countries.models import BranchCountry
from django.db.models import QuerySet
from web.factories.menu import MenuFactory
from web.factories.pages import PageFactory
from web.factories.partners import OrganizerFactory, PartnerFactory


def create_pages(branch: Branch):
    branch_countries: QuerySet[BranchCountry] = BranchCountry.objects.filter(
        branch=branch
    )
    reverse_mapping: dict[str, list[str]] = dict()

    for branch_country in branch_countries:
        for lang in branch_country.languages:
            if lang in reverse_mapping:
                reverse_mapping[lang].append(branch_country.country)
            else:
                reverse_mapping[lang] = [branch_country.country]

    for lang, countries in reverse_mapping.items():
        for slug in ["rules", "about", "contact"]:
            PageFactory(
                language=lang,
                branch=branch,
                slug=slug,
                countries=countries,
            )
            MenuFactory(
                language=lang,
                branch=branch,
                url=slug,
                countries=countries,
            )
        MenuFactory(
            language=lang,
            branch=branch,
            countries=countries,
            external=True,
        )


def create_partners():
    PartnerFactory.create_batch(20)
    OrganizerFactory.create_batch(20)
