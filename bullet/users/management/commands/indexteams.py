from django.core.management.base import BaseCommand
from users.models import Team

from bullet import search


class Command(BaseCommand):
    help = "Send teams to Meilisearch for indexing"

    def handle(self, *args, **options):
        teams = []
        for t in Team.objects.all():
            teams.append(t.for_search())

        search.client.index("teams").add_documents(teams)
