from django.conf import settings
from web.factories.pages import PageFactory


def create_pages(branch):
    for lang, _ in settings.LANGUAGES:
        for slug in ["rules", "about", "contact"]:
            PageFactory(language=lang, branch=branch, slug=slug)
