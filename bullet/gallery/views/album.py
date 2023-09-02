from competitions.models import Competition
from countries.models import BranchCountry
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from gallery.models import Album, Photo


class GalleryCompetitionMixin:
    @property
    def competition(self):
        if not hasattr(self, "_competition"):
            self._competition = get_object_or_404(
                Competition.objects.for_photograph(
                    self.request.user, self.request.BRANCH
                ),
                branch=self.request.BRANCH,
                number=self.kwargs["competition_number"],
            )
        return self._competition

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition_number"] = self.competition.number
        ctx["competition"] = self.competition
        return ctx


class PhotoView(GalleryCompetitionMixin, ListView):
    template_name = "album.html"

    def get_queryset(self):
        return Photo.objects.filter(
            album__competition=self.competition, album__country=self.country
        )

    def dispatch(self, request, *args, **kwargs):
        self.country: str = kwargs.get("country")
        if self.country:
            self.country = self.country.upper()
            get_object_or_404(
                BranchCountry, branch=request.BRANCH, country=self.country
            )

        self.album = get_object_or_404(
            Album,
            competition=self.competition,
            country=self.country,
            title=kwargs.get("title"),
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["country"] = self.country
        ctx["competition"] = self.competition
        ctx["album"] = self.album

        return ctx
