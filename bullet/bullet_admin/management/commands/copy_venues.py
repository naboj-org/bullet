from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from competitions.models import Competition, Category, Venue
from countries.models import BranchCountry


class Command(BaseCommand):
    help = "Copy venues from one competition to another, using categories from the new competition"

    def add_arguments(self, parser):
        parser.add_argument(
            "source_competition_id",
            type=int,
            help="ID of the source competition to copy venues from",
        )
        parser.add_argument(
            "target_competition_id",
            type=int,
            help="ID of the target competition to copy venues to",
        )

    def handle(self, *args, **options):
        source_competition_id = options["source_competition_id"]
        target_competition_id = options["target_competition_id"]

        try:
            source_competition = Competition.objects.get(id=source_competition_id)
            target_competition = Competition.objects.get(id=target_competition_id)
        except Competition.DoesNotExist as e:
            raise CommandError(f"Competition not found: {e}")

        self.stdout.write(
            f"Copying venues from '{source_competition.name}' to '{target_competition.name}'"
        )

        # Get all venues from source competition
        source_venues = Venue.objects.for_competition(
            source_competition
        ).select_related("category")
        source_venue_count = source_venues.count()

        if source_venue_count == 0:
            self.stdout.write(
                self.style.WARNING("No venues found in source competition")
            )
            return

        # Get all categories from target competition
        target_categories = {
            cat.identifier: cat
            for cat in Category.objects.filter(competition=target_competition)
        }
        target_category_count = len(target_categories)

        if target_category_count == 0:
            self.stdout.write(
                self.style.WARNING("No categories found in target competition")
            )
            return

        self.stdout.write(f"Found {source_venue_count} venues in source competition")
        self.stdout.write(
            f"Found {target_category_count} categories in target competition"
        )

        with transaction.atomic():
            copied_count = 0
            skipped_count = 0

            for source_venue in source_venues:
                source_category = source_venue.category
                target_category = target_categories.get(source_category.identifier)

                if not target_category:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping venue '{source_venue.name}': "
                            f"No matching category found for '{source_category.identifier}'"
                        )
                    )
                    skipped_count += 1
                    continue

                source_venue.category = target_category
                source_venue.id = None
                source_venue.local_start = None
                source_venue.save()
                copied_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Copy completed: {copied_count} venues copied, {skipped_count} venues skipped"
                )
            )
