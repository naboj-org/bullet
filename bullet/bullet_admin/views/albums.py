from datetime import datetime, timezone

from countries.logic.detection import get_country_language_from_request
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from gallery.models import Album, Photo
from PIL import Image

from bullet_admin.access import PhotoUploadAccess
from bullet_admin.forms.album import AlbumForm
from bullet_admin.mixins import RedirectBackMixin
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericDelete, GenericForm, GenericList


class AlbumListView(PhotoUploadAccess, GenericList, ListView):
    create_url = reverse_lazy("badmin:album_create")
    labels = {"slug": "URL suffix (slug)"}
    fields = ["title", "slug", "country", "photos"]
    field_templates = {
        "country": "bullet_admin/partials/country.html",
        "photos": "bullet_admin/albums/photos.html",
    }

    def get_queryset(self):
        return Album.objects.filter(competition=get_active_competition(self.request))

    def get_edit_url(self, album: Album) -> str:
        return reverse("badmin:album_edit", args=[album.pk])

    def get_delete_url(self, album: Album) -> str:
        return reverse("badmin:album_delete", args=[album.pk])

    def get_view_url(self, album: Album) -> str:
        country, language = self.detection
        return reverse(
            "archive_album",
            kwargs={
                "b_country": country,
                "b_language": language,
                "competition_number": album.competition.number,
                "slug": album.slug,
            },
        )

    def dispatch(self, request, *args, **kwargs):
        self.detection = get_country_language_from_request(self.request)
        if not self.detection:
            return redirect("country_selector")

        return super().dispatch(request, *args, **kwargs)


class AlbumFormMixin(GenericForm):
    form_class = AlbumForm
    form_multipart = True

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def form_valid(self, form):
        album: Album = form.save(commit=False)
        album.competition = get_active_competition(self.request)
        for file in form.cleaned_data["photo_files"]:
            photo = Photo(album=album, image=file)

            im = Image.open(file)
            taken_at: str | None = im.getexif().get(36867)
            if taken_at:
                photo.taken_at = datetime.strptime(
                    taken_at, "%Y:%m:%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)

            photo.save()
        album.save()
        return HttpResponseRedirect(self.get_success_url())


class AlbumUpdateView(PhotoUploadAccess, RedirectBackMixin, AlbumFormMixin, UpdateView):
    form_title = "Edit album"

    def get_queryset(self):
        return Album.objects.filter(competition__branch=self.request.BRANCH)

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.success(self.request, "Album edited successfully.")
        return ret


class AlbumCreateView(PhotoUploadAccess, RedirectBackMixin, AlbumFormMixin, CreateView):
    form_title = "New album"

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.success(self.request, "Album created successfully.")
        return ret


class AlbumDeleteView(PhotoUploadAccess, RedirectBackMixin, GenericDelete, DeleteView):
    model = Album

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, "Album deleted successfully.")
        return HttpResponseRedirect(self.get_success_url())
