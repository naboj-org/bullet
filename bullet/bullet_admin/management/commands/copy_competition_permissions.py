from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from competitions.models import Competition, Venue
from bullet_admin.models import CompetitionRole


class Command(BaseCommand):
    help = (
        "Copy permissions from one competition to another, mapping venues by shortcodes"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "source_competition_id",
            type=int,
            help="ID of the source competition to copy permissions from",
        )
        parser.add_argument(
            "destination_competition_id",
            type=int,
            help="ID of the destination competition to copy permissions to",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be copied without actually making changes",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing permissions in destination competition",
        )

    def handle(self, *args, **options):
        source_id = options["source_competition_id"]
        dest_id = options["destination_competition_id"]
        dry_run = options["dry_run"]
        overwrite = options["overwrite"]

        try:
            source_competition = Competition.objects.get(id=source_id)
            dest_competition = Competition.objects.get(id=dest_id)
        except Competition.DoesNotExist as e:
            raise CommandError(f"Competition not found: {e}")

        if source_competition.branch != dest_competition.branch:
            raise CommandError(
                f"Competitions must be from the same branch. "
                f"Source: {source_competition.branch}, "
                f"Destination: {dest_competition.branch}"
            )

        self.stdout.write(
            f"Copying permissions from {source_competition} to {dest_competition}"
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        try:
            with transaction.atomic():
                self.copy_permissions(
                    source_competition, dest_competition, dry_run, overwrite
                )
        except Exception as e:
            raise CommandError(f"Error copying permissions: {e}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("Permissions copied successfully!"))

    def copy_permissions(self, source_comp, dest_comp, dry_run, overwrite):
        """Copy competition permissions from source to destination"""

        # Get venue mapping by shortcode
        venue_mapping = self.create_venue_mapping(source_comp, dest_comp)

        # Get all source competition roles
        source_roles = CompetitionRole.objects.filter(competition=source_comp)

        self.stdout.write(f"Found {source_roles.count()} roles to copy")

        copied_count = 0
        skipped_count = 0

        for source_role in source_roles:
            # Check if destination role already exists
            dest_role_exists = CompetitionRole.objects.filter(
                user=source_role.user, competition=dest_comp
            ).exists()

            if dest_role_exists and not overwrite:
                self.stdout.write(f"Skipping {source_role.user} - role already exists")
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f"Would copy role for {source_role.user}")
                copied_count += 1
                continue

            # Create or update destination role
            dest_role = CompetitionRole.objects.create(
                user=source_role.user,
                competition=dest_comp,
                countries=source_role.countries,
                can_delegate=source_role.can_delegate,
                is_operator=source_role.is_operator,
            )

            self.map_role_venues(source_role, dest_role, venue_mapping)

            copied_count += 1
            self.stdout.write(f"Copied role for {source_role.user}")

        self.stdout.write(
            f"\nSummary: {copied_count} roles copied, {skipped_count} skipped"
        )

    def create_venue_mapping(self, source_comp, dest_comp):
        """Create mapping of venues by shortcode between competitions"""

        # Get all venues from both competitions
        source_venues = Venue.objects.filter(category__competition=source_comp)
        dest_venues = Venue.objects.filter(category__competition=dest_comp)

        # Create mapping dictionary: shortcode -> destination venue
        venue_mapping = {}

        for source_venue in source_venues:
            # Find matching venue in destination by shortcode
            dest_venue = dest_venues.filter(shortcode=source_venue.shortcode).first()

            if dest_venue:
                venue_mapping[source_venue.id] = dest_venue
                self.stdout.write(
                    f"Mapped venue: {source_venue.name} ({source_venue.shortcode}) "
                    f"-> {dest_venue.name}"
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"No matching venue found for shortcode: {source_venue.shortcode}"
                    )
                )

        return venue_mapping

    def map_role_venues(self, source_role, dest_role, venue_mapping):
        """Map venues for a competition role from source to destination"""

        if not source_role.venues.exists():
            return

        mapped_venues = []
        unmapped_count = 0

        for source_venue in source_role.venues.all():
            if source_venue.id in venue_mapping:
                dest_venue = venue_mapping[source_venue.id]
                mapped_venues.append(dest_venue)
            else:
                unmapped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not map venue {source_venue.name} "
                        f"for user {source_role.user}"
                    )
                )

        # Clear existing venues and add mapped ones
        dest_role.venue_objects.clear()
        dest_role.venue_objects.add(*mapped_venues)

        if unmapped_count > 0:
            self.stdout.write(
                f"User {dest_role.user}: "
                f"{len(mapped_venues)} venues mapped, {unmapped_count} unmapped"
            )
        else:
            self.stdout.write(
                f"User {dest_role.user}: "
                f"{len(mapped_venues)} venues mapped successfully"
            )

