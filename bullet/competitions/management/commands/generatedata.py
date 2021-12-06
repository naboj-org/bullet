from competitions.factories.generate import create_base, create_competition
from competitions.models import Competition
from django.core.management import BaseCommand
from django.db import transaction
from education.factories.generate import create_education
from web.factories.generate import create_pages


class Command(BaseCommand):
    help = "Generates some testing data"

    @transaction.atomic
    def handle(self, *args, **options):
        create_base()
        create_education()
        create_pages(branch=Competition.Branch.PHYSICS)
        create_competition(branch=Competition.Branch.PHYSICS)
