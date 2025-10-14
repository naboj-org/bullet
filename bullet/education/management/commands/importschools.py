import argparse

from django.core.management.base import BaseCommand
from education.importers import IMPORTERS


class Command(BaseCommand):
    help = "Import schools from dataset"

    def add_arguments(self, parser):
        parser.add_argument("importer", type=str)
        parser.add_argument("file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        if options["importer"] not in IMPORTERS:
            self.stderr.write(
                self.style.ERROR(f"Importer {options['importer']} is not valid.")
            )
            raise SystemExit(1)

        importer_cls = IMPORTERS[options["importer"]]
        importer = importer_cls(options["file"])
        importer.prepare_types()
        self.stderr.write(self.style.SUCCESS("Prepared school types."))

        res = importer.import_schools()
        self.stderr.write(
            self.style.SUCCESS(f"Imported {res.created + res.updated} schools.")
        )
        self.stderr.write(f"Created: {res.created} Updated: {res.updated}")
        self.stderr.write(f"Lost: {len(res.lost_identifiers)}")

        for lost in res.lost_identifiers:
            self.stdout.write(self.style.WARNING(lost))
