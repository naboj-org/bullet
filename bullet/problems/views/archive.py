from competitions.models import Competition
from django.shortcuts import get_object_or_404
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
                Competition,
                branch=self.request.BRANCH,
                number=self.kwargs["competition_number"],
            )
        return self._competition

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition_number"] = self.competition.number
        return ctx


class ArchiveResultsSelectView(ArchiveCompetitionMixin, ResultsSelectView):
    pass


class ArchiveCategoryResultsView(ArchiveCompetitionMixin, CategoryResultsView):
    pass


class ArchiveVenueResultsView(ArchiveCompetitionMixin, VenueResultsView):
    pass
