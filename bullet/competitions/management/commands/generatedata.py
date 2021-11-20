from competitions.factories.generate import create_base, create_competition
from competitions.models import Competition
from django.core.management import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Generates some testing data"

    @transaction.atomic
    def handle(self, *args, **options):
        create_base()
        create_competition(branch=Competition.Branch.PHYSICS)
