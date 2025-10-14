from bullet_admin.access import MixinProtocol
from bullet_admin.utils import get_active_branch
from competitions.models import Competition
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import ListView
from problems.views.archive import ArchiveCompetitionMixin

from gallery.models import Album, Photo


class GalleryCompetitionMixin(ArchiveCompetitionMixin, MixinProtocol):
    @cached_property
    def competition(self):
        return get_object_or_404(
            Competition.objects.filter(branch=get_active_branch(self.request)),
            number=self.kwargs["competition_number"],
        )


class AlbumView(GalleryCompetitionMixin, ListView):
    template_name = "gallery/album.html"

    def get_queryset(self):
        return Photo.objects.filter(album=self.album).order_by("taken_at")

    def dispatch(self, request, *args, **kwargs):
        self.album = get_object_or_404(
            Album,
            competition=self.competition,
            slug=kwargs.get("slug"),
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["album"] = self.album
        return ctx


class AlbumListView(GalleryCompetitionMixin, ListView):
    template_name = "gallery/list.html"

    def get_queryset(self):
        return Album.objects.filter(competition=self.competition)
