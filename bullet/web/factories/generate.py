from web.factories.pages import PageFactory

from bullet.constants import Languages


def create_pages(branch):
    for lang in Languages.values:
        for slug in ["rules", "about", "contact"]:
            PageFactory(language=lang, branch=branch, url=slug)
