from competitions.branches import Branches
from competitions.factories.generate import create_competition
from countries.factories.generate import create_branch_countries
from django.core import management
from django.core.management import BaseCommand
from django.db import transaction
from education.factories.generate import create_education
from problems.factories.generate import create_problems
from web.factories.generate import create_pages, create_partners


class Command(BaseCommand):
    help = "Generates some testing data"

    @transaction.atomic
    def handle(self, *args, **options):
        create_education()
        create_branch_countries(branch=Branches["physics"])
        create_pages(branch=Branches["physics"])
        competition_physics = create_competition(branch=Branches["physics"])
        create_problems(competition_physics)
        create_branch_countries(branch=Branches["chemistry"])
        create_pages(branch=Branches["chemistry"])
        competition_chemistry = create_competition(branch=Branches["chemistry"])
        create_problems(competition_chemistry)
        create_partners()
        management.call_command("indexschools")
