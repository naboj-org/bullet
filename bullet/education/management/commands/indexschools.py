from django.core.management.base import BaseCommand
from education.models import School

from bullet import search


class Command(BaseCommand):
    help = "Send schools to Meilisearch for indexing"

    def handle(self, *args, **options):
        schools = []
        for s in School.objects.filter(is_legacy=False).all():
            schools.append(s.for_search())

        search.client.index("schools").update_settings(
            {
                "filterableAttributes": ["country", "is_hidden"],
                "synonyms": {
                    "zš": ["základná škola", "základní škola"],
                    "základná škola": ["zš"],
                    "základní škola": ["zš"],
                    "sš": ["stredná škola", "strední škola", "srednja škola"],
                    "stredná škola": ["sš"],
                    "strední škola": ["sš"],
                    "srednja škola": ["sš"],
                    "oš": ["osnovna škola"],
                    "osnovna škola": ["oš"],
                },
            }
        )

        search.client.index("schools").add_documents(schools)
