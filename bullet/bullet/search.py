from functools import cache

import meilisearch
from django.conf import settings
from django.core.paginator import Page

enabled = bool(settings.MEILISEARCH_URL)
client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)


class MeiliQuerySet:
    """
    MeiliQuerySet provides a Paginator-compatible API to allow the use of Meilisearch
    results in ListViews.

    When using our admin_paginator, it is advisable to use `nerf_page()` on the Page
    object.
    """

    def __init__(self, queryset, index, search_term, opt_params=None):
        self.queryset = queryset
        self.index = index
        self.search_term = search_term
        self.opt_params = opt_params

    @cache
    def get_results(self, offset=0, limit=20):
        params = self.opt_params or {}
        params["offset"] = offset
        params["limit"] = limit

        res = client.index(self.index).search(self.search_term, params)

        hits = res["hits"]
        ids = [hit["id"] for hit in hits]
        objects = self.queryset.filter(id__in=ids)
        objects = sorted(objects, key=lambda o: ids.index(o.id))
        return objects

    def __len__(self):
        return 10**10

    def __getitem__(self, item):
        if not isinstance(item, slice):
            raise ValueError(
                "Instance of MeiliQuerySet does not support getting exact items."
            )

        return self.get_results(item.start, item.stop - item.start)


class DumbPage(Page):
    """
    A dumb implementation of Page object that does not need to know the
    total number of pages.
    """

    def __repr__(self):
        return f"<Page {self.number} of many>"

    def __len__(self):
        return len(self.object_list)

    def has_next(self):
        return len(self) == self.paginator.per_page

    def next_page_number(self):
        return self.number + 1

    def previous_page_number(self):
        return self.number - 1


def nerf_page(page: Page) -> DumbPage:
    """
    Converts a normal Page object into a dumb one.
    """
    return DumbPage(page.object_list, page.number, page.paginator)
