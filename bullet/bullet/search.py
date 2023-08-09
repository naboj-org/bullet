import meilisearch
from django.conf import settings

enabled = bool(settings.MEILISEARCH_URL)
client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)
