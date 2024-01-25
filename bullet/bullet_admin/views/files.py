import os
import shutil
from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from bullet_admin.forms.files import (
    FileDeleteForm,
    FileUploadForm,
    FolderCreateForm,
    TestForm,
)
from bullet_admin.mixins import TranslatorRequiredMixin
from bullet_admin.views import GenericForm


def get_path(request, path):
    branch_root = os.path.join("files", request.BRANCH.identifier)
    abs_path = os.path.normpath(os.path.join(branch_root, path))

    if os.path.commonpath([branch_root, abs_path]) != branch_root:
        raise PermissionDenied()

    return branch_root, abs_path


class FileTreeView(TranslatorRequiredMixin, TemplateView):
    template_name = "bullet_admin/files/tree.html"

    def get_parents(self):
        path = self.request.GET.get("path", "")
        path = Path(path)
        parents = path.parents
        parents = filter(lambda p: p.name != "", parents)
        parents = map(lambda p: (p.name, str(p)), parents)
        parents = list(parents)[::-1]
        parents.append((path.name, str(path)))
        return parents

    def get_files(self):
        branch_root, abs_path = get_path(self.request, self.request.GET.get("path", ""))

        if not default_storage.exists(abs_path):
            return []

        real_path = default_storage.path(abs_path)
        if os.path.isfile(real_path):
            return []

        dirs, files = default_storage.listdir(abs_path)
        dirs = [(d, True) for d in sorted(dirs)]
        files = [(f, False) for f in sorted(files)]
        files = dirs + files

        output = []
        for file, is_dir in files:
            file_path = os.path.join(abs_path, file)
            output.append(
                {
                    "name": file,
                    "path": os.path.relpath(file_path, branch_root),
                    "is_dir": is_dir,
                    "size": default_storage.size(file_path) if not is_dir else 0,
                    "public_path": default_storage.url(file_path),
                }
            )

        return output

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["files"] = self.get_files()
        ctx["parents"] = self.get_parents()
        return ctx


class FolderCreateView(TranslatorRequiredMixin, GenericForm, FormView):
    form_title = "Create new folder"
    form_class = FolderCreateForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["initial_path"] = self.request.GET.get("path", "")
        return kw

    def form_valid(self, form):
        branch_root, path = get_path(self.request, form.cleaned_data["path"])
        folder = os.path.normpath(os.path.join(path, form.cleaned_data["name"]))
        if os.path.commonpath([folder, branch_root]) != branch_root:
            raise PermissionDenied()

        # Django Storage API does not support mkdir :(
        folder_path = default_storage.path(folder)
        os.makedirs(folder_path, exist_ok=True)
        return HttpResponseRedirect(
            reverse("badmin:file_tree") + "?path=" + os.path.relpath(path, branch_root)
        )


class FileUploadView(TranslatorRequiredMixin, GenericForm, FormView):
    form_title = "Upload file"
    form_multipart = True
    form_class = FileUploadForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["initial_path"] = self.request.GET.get("path", "")
        return kw

    def form_valid(self, form):
        branch_root, path = get_path(self.request, form.cleaned_data["path"])

        file_name = form.cleaned_data["file"].name
        if form.cleaned_data["name"]:
            file_name = form.cleaned_data["name"]

        file_path = os.path.normpath(os.path.join(path, file_name))
        if os.path.commonpath([file_path, branch_root]) != branch_root:
            raise PermissionDenied()

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        default_storage.save(file_path, form.cleaned_data["file"])
        return HttpResponseRedirect(
            reverse("badmin:file_tree") + "?path=" + os.path.relpath(path, branch_root)
        )


class FileDeleteView(TranslatorRequiredMixin, GenericForm, FormView):
    form_title = "Delete file"
    form_class = FileDeleteForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["initial_path"] = self.request.GET.get("path", "")
        return kw

    def form_valid(self, form):
        branch_root, path = get_path(self.request, form.cleaned_data["path"])

        # Django Storage API cannot delete whole folders :(
        folder_path = default_storage.path(path)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        else:
            default_storage.delete(path)
        return HttpResponseRedirect(reverse("badmin:file_tree"))


class TreeFieldView(FileTreeView):
    def get_template_names(self):
        if self.request.GET.get("selected"):
            return ["bullet_admin/files/tree_field.html"]
        return ["bullet_admin/files/tree_field_open.html"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.GET.get("selected"):
            ctx["field"] = {
                "name": self.request.GET.get("field"),
                "value": self.request.GET.get("path"),
            }
        return ctx


class TreeFieldTestView(GenericForm, FormView):
    form_class = TestForm

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)
