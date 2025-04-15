from countries.logic.detection import get_country_language_from_request
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView
from gallery.models import Album, Photo

from bullet_admin.access import PhotoUploadAccess
from bullet_admin.forms.album import AlbumForm, AlbumUploadForm
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

    table_labels = {"slug": "URL suffix"}
    table_fields = ["title", "slug", "country"]
    table_field_templates = {
        "country": "bullet_admin/partials/field__country.html",
    }

    def get_queryset(self):
        return Album.objects.filter(competition=get_active_competition(self.request))

    def get_row_links(self, object) -> list[Link]:
        assert self.detection
        country, language = self.detection
        view = reverse(
            "archive_album",
            kwargs={
                "b_country": country,
                "b_language": language,
                "competition_number": object.competition.number,
                "slug": object.slug,
            },
        )

        return [
            Link(
                "blue",
                "mdi:image-outline",
                "Photos",
                reverse("badmin:album_photo_list", args=[object.pk]),
            ),
            EditIcon(reverse("badmin:album_update", args=[object.pk])),
            ExternalViewIcon(view),
            DeleteIcon(reverse("badmin:album_delete", args=[object.pk])),
        ]

    def dispatch(self, request, *args, **kwargs):
        self.detection = get_country_language_from_request(self.request)
        if not self.detection:
            return redirect("country_selector")

        return super().dispatch(request, *args, **kwargs)


class AlbumFormMixin(GenericForm):
    form_class = AlbumForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw


class AlbumUpdateView(PhotoUploadAccess, AlbumFormMixin, RedirectBackMixin, UpdateView):
    form_title = "Edit album"

    def get_default_success_url(self):
        return reverse("badmin:album_update", kwargs={"pk": self.object.id})

    def get_queryset(self):
        return Album.objects.filter(competition__branch=self.request.BRANCH)  # type:ignore

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.success(self.request, "Album edited successfully.")
        return ret


class AlbumCreateView(PhotoUploadAccess, AlbumFormMixin, CreateView):
    form_title = "New album"

    def get_success_url(self):
        return reverse("badmin:album_photo_list", kwargs={"pk": self.object.id})

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


class AlbumPhotoListView(PhotoUploadAccess, GenericList, ListView):
    table_fields = ["image"]
    table_field_templates = {"image": "bullet_admin/albums/field__image.html"}

    def get_list_links(self) -> list[Link]:
        return [
            Link(
                "green",
                "mdi:upload",
                "Upload photos",
                reverse("badmin:album_upload", args=[self.album.id]),
            )
        ]

    def get_row_links(self, object) -> list[Link]:
        return [
            DeleteIcon(
                reverse("badmin:album_photo_delete", args=[self.album.id, object.id])
            )
        ]

    @cached_property
    def album(self):
        return get_object_or_404(Album, id=self.kwargs["pk"])

    def get_queryset(self):
        return Photo.objects.filter(album=self.album)


class AlbumPhotoDeleteView(PhotoUploadAccess, GenericDelete, DeleteView):
    @cached_property
    def album(self):
        return get_object_or_404(Album, id=self.kwargs["album_pk"])

    def get_queryset(self):
        return Photo.objects.filter(album=self.album)

    def get_success_url(self):
        return reverse("badmin:album_photo_list", kwargs={"pk": self.album.id})


class AlbumUploadView(PhotoUploadAccess, GenericForm, FormView):
    form_class = AlbumUploadForm
    form_title = "Upload photos"
    form_multipart = True
    form_submit_label = "Upload"
    form_submit_icon = "mdi:upload"

    def get_success_url(self):
        return reverse("badmin:album_photo_list", kwargs={"pk": self.album.id})

    @cached_property
    def album(self):
        return get_object_or_404(Album, id=self.kwargs["pk"])

    def form_valid(self, form):
        for file in form.cleaned_data["photo_files"]:
            photo = Photo(album=self.album, image=file)
            photo.read_taken_at()
            photo.save()

        messages.success(self.request, "Photos uploaded successfully.")
        return HttpResponseRedirect(self.get_success_url())
