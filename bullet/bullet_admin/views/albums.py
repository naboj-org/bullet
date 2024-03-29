from datetime import datetime, timezone

from countries.models import BranchCountry
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, UpdateView
from gallery.models import Album, Photo
from PIL import Image

from bullet_admin.access import PhotoUploadAccess
from bullet_admin.forms.album import AlbumForm
from bullet_admin.views import GenericForm


class AlbumListView(PhotoUploadAccess, ListView):
    template_name = "bullet_admin/albums/list.html"
    paginate_by = 100

    def get_queryset(self):
        return Album.objects.filter(competition__branch=self.request.BRANCH)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["album_count"] = Album.objects.filter(
            competition__branch=self.request.BRANCH
        ).count()

        country = BranchCountry.objects.filter(branch=self.request.BRANCH).first()
        ctx["country"] = country.country.code.lower()
        ctx["language"] = country.languages[0]

        return ctx


class AlbumFormMixin(GenericForm):
    form_class = AlbumForm
    form_multipart = True

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw


class AlbumUpdateView(PhotoUploadAccess, AlbumFormMixin, UpdateView):
    form_title = "Edit album"

    def form_valid(self, form):
        album: Album = form.save(commit=False)
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
        messages.success(self.request, "Album edited successfully.")
        return redirect("badmin:album_list")

    def get_queryset(self):
        return Album.objects.filter(competition__branch=self.request.BRANCH)


class AlbumCreateView(PhotoUploadAccess, AlbumFormMixin, CreateView):
    form_title = "New album"

    def form_valid(self, form):
        album: Album = form.save(commit=False)
        album.save()

        for photo in form.cleaned_data["photo_files"]:
            Photo(album=album, image=photo).save()

        messages.success(self.request, "Album created successfully.")
        return redirect("badmin:album_list")
