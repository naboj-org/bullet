import os
from typing import List, TypeVar, Type

from django.core.management import BaseCommand
from django.db import transaction

from competitions.management.commands.old_data_models import OldSite
from competitions.models import Site


T = TypeVar("T")


def load_objects(cls: Type[T], folder_path) -> List[T]:
    with open(os.path.join(folder_path, f'{cls.table_name}.json')) as f:
        content = f.read()

    l: List[cls] = cls.schema().loads(content, many=True)

    return l


def migrate_sites(folder_path) -> List[Site]:
    new_sites = [
        Site(
            name=old_site.name,
            short_name=old_site.name
        )
        for old_site in load_objects(OldSite, folder_path)
    ]
    return Site.objects.bulk_create(new_sites)


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        migrate_sites('old_dumps')
