from countries.models import BranchCountry
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

_country_cache = set()


def get_country_cache() -> set[tuple[int, str, str]]:
    if not len(_country_cache):
        countries = BranchCountry.objects.all()

        for c in countries:
            for lang in c.languages:
                _country_cache.add((c.branch, c.country.code.lower(), lang.lower()))

    return _country_cache


@receiver(post_save, sender=BranchCountry)
@receiver(post_delete, sender=BranchCountry)
def reset_cache(*args, **kwargs):
    _country_cache.clear()
