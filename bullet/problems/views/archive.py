import os.path

from competitions.models import Competition
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django.views.generic import ListView
from problems.models import ProblemStatement
from problems.views.results import (
    CategoryResultsView,
    ResultsSelectView,
    VenueResultsView,
)


class ArchiveCompetitionMixin:
    @property
    def competition(self):
        if not hasattr(self, "_competition"):
            self._competition = get_object_or_404(
                Competition.objects.for_user(self.request.user, self.request.BRANCH),
                branch=self.request.BRANCH,
                number=self.kwargs["competition_number"],
            )
        return self._competition

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition_number"] = self.competition.number
        ctx["competition"] = self.competition
        return ctx


class ArchiveResultsSelectView(ArchiveCompetitionMixin, ResultsSelectView):
    pass


class ArchiveCategoryResultsView(ArchiveCompetitionMixin, CategoryResultsView):
    pass


class ArchiveVenueResultsView(ArchiveCompetitionMixin, VenueResultsView):
    pass


class ProblemStatementView(ArchiveCompetitionMixin, ListView):
    template_name = "archive/problems.html"

    def get_queryset(self):
        return ProblemStatement.objects.filter(
            problem__competition=self.competition, language=get_language()
        ).prefetch_related(
            "problem__category_problems", "problem__category_problems__category"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pdf_file = os.path.join(
            "statements",
            self.request.BRANCH.identifier,
            f"{self.competition.number}-{get_language()}.pdf",
        )
        if default_storage.exists(pdf_file):
            ctx["pdf"] = default_storage.url(pdf_file)
        return ctx
