from countries.models import BranchCountry
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from gallery.models import Album, Photo
from problems.views.archive import ArchiveCompetitionMixin


class PhotoView(ArchiveCompetitionMixin, ListView):
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
