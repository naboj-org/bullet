from bullet_admin.access import AdminAccess, PhotoUploadAccess
from bullet_admin.forms.album import AlbumForm
from bullet_admin.views import GenericForm
from countries.models import BranchCountry
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from gallery.models import Album, Photo


class AlbumListView(AdminAccess, ListView):
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


class Photoformmixin(GenericForm):
    form_class = AlbumForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw


class AlbumUpdateView(PhotoUploadAccess, Photoformmixin, UpdateView):
    form_title = "Edit album"

    def form_valid(self, form):
        album: Album = form.save(commit=False)
        for photo in form.cleaned_data["photo_files"]:
            Photo(album=album, image=photo).save()
        album.save()
        messages.success(self.request, "Album edited successfully.")
        return redirect("badmin:album_list")

    def get_queryset(self):
        return Album.objects.filter(competition__branch=self.request.BRANCH)

    def get_success_url(self):
        return reverse("badmin:album_list")


class AlbumCreateView(PhotoUploadAccess, Photoformmixin, CreateView):
    form_title = "New album"

    def form_valid(self, form):
        album: Album = form.save(commit=False)
        album.save()

        for photo in form.cleaned_data["photo_files"]:
            Photo(album=album, image=photo).save()

        messages.success(self.request, "Album created successfully.")

        return redirect("badmin:album_list")

    def get_success_url(self):
        return reverse("badmin:album_list")
