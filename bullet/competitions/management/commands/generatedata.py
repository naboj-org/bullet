from competitions.branches import Branches
from competitions.factories.generate import (
    create_ended_competition,
    create_registration_in_progress_competition,
)
from countries.factories.branchcountry import BranchCountryFactory
from django.core import management
from django.core.management import BaseCommand
from django.db import transaction
from education.factories.generate import create_education
from problems.factories.generate import create_problems
from users.factories.generate import create_users
from web.factories.generate import create_pages, create_partners

from bullet import search


class Command(BaseCommand):
    help = "Generates some testing data"

    @transaction.atomic
    def handle(self, *args, **options):
        search.enabled = False
        create_education()
        BranchCountryFactory.create_batch(20)
        create_pages(branch=Branches["math"])
        create_pages(branch=Branches["physics"])
        create_pages(branch=Branches["junior"])
        create_pages(branch=Branches["chemistry"])
        for _ in range(5):
            ended_competition = create_ended_competition()
            create_problems(ended_competition)
        competition_physics = create_registration_in_progress_competition(
            branch=Branches["physics"]
        )
        create_problems(competition_physics)

        create_partners()
        create_users(competition_physics)
        management.call_command("indexschools")
