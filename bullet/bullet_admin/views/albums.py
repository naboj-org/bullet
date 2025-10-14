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
from bullet_admin.views import GenericDelete, GenericForm
from bullet_admin.views.generic.links import (
    DeleteIcon,
    EditIcon,
    ExternalViewIcon,
    Link,
    NewLink,
)
from bullet_admin.views.generic.list import GenericList


class AlbumListView(PhotoUploadAccess, GenericList, ListView):
    list_links = [
        NewLink("album", reverse_lazy("badmin:album_create")),
    ]

    table_labels = {"slug": "URL suffix (slug)"}
    table_fields = ["title", "slug", "country", "photos"]
    table_field_templates = {
        "country": "bullet_admin/partials/field__country.html",
        "photos": "bullet_admin/albums/field__photos.html",
    }

    def get_queryset(self):
        return Album.objects.filter(competition=get_active_competition(self.request))

    def get_row_links(self, obj) -> list[Link]:
        assert self.detection
        country, language = self.detection
        view = reverse(
            "archive_album",
            kwargs={
                "b_country": country,
                "b_language": language,
                "competition_number": obj.competition.number,
                "slug": obj.slug,
            },
        )

        return [
            EditIcon(reverse("badmin:album_edit", args=[obj.pk])),
            ExternalViewIcon(view),
            DeleteIcon(reverse("badmin:album_delete", args=[obj.pk])),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.detection = get_country_language_from_request(self.request)
        if not self.detection:
            return redirect("country_selector")

        return super().dispatch(request, *args, **kwargs)


class AlbumFormMixin(RedirectBackMixin, GenericForm):
    form_class = AlbumForm
    form_multipart = True

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def form_valid(self, form):
        album: Album = form.save(commit=False)
        self.object = album
        album.competition = get_active_competition(self.request)
        album.save()
        for file in form.cleaned_data["photo_files"]:
            photo = Photo(album=album, image=file)

            im = Image.open(file)
            taken_at: str | None = im.getexif().get(36867)
            if taken_at:
                photo.taken_at = datetime.strptime(
                    taken_at, "%Y:%m:%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)

            photo.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_default_success_url(self):
        return reverse("badmin:album_edit", kwargs={"pk": self.object.id})


class AlbumUpdateView(PhotoUploadAccess, AlbumFormMixin, UpdateView):
    form_title = "Edit album"

    def get_queryset(self):
        return Album.objects.filter(competition__branch=self.request.BRANCH)

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.success(self.request, "Album edited successfully.")
        return ret


class AlbumCreateView(PhotoUploadAccess, AlbumFormMixin, CreateView):
    form_title = "New album"

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.success(self.request, "Album created successfully.")
        return ret


class AlbumDeleteView(PhotoUploadAccess, RedirectBackMixin, GenericDelete, DeleteView):
    model = Album
    default_success_url = reverse_lazy("badmin:album_list")

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, "Album deleted successfully.")
        return HttpResponseRedirect(self.get_success_url())
