from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView
from problems.logic.upload import ProblemImportError

from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.archive import ProblemImportForm, ProblemUploadForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm


class ProblemImportView(BranchAdminAccess, GenericForm, FormView):
    form_class = ProblemImportForm
    template_name = "bullet_admin/archive/import.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        try:
            form.save()
            messages.success(self.request, "Successfully imported problems.")
        except ProblemImportError as e:
            messages.error(self.request, e)
        return redirect("badmin:archive_import")


class ProblemPDFUploadView(BranchAdminAccess, GenericForm, FormView):
    form_class = ProblemUploadForm
    form_title = "Upload problems"
    form_multipart = True

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Successfully uploaded problems.")
        return redirect("badmin:archive_problem_upload")
