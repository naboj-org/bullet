from django.core.management.base import BaseCommand
from education.models import School

from bullet import search


class Command(BaseCommand):
    help = "Send schools to Meilisearch for indexing"

    def handle(self, *args, **options):
        schools = []
        for s in School.objects.all():
            schools.append(s.for_search())

        search.client.index("schools").update_settings(
            {
                "filterableAttributes": ["country"],
            }
        )

        search.client.index("schools").add_documents(schools)
