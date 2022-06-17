from competitions.branches import Branches
from competitions.factories.generate import create_base, create_competition
from countries.factories.generate import create_branch_countries
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
        create_branch_countries(branch=Branches["physics"])
        create_pages(branch=Branches["physics"])
        create_competition(branch=Branches["physics"])
