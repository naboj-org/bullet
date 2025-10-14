from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView
from problems.logic.upload import ProblemImportError

from bullet_admin.access import (
    PermissionCheckMixin,
    is_branch_admin,
    is_country_admin,
)
from bullet_admin.forms.archive import ProblemImportForm, ProblemUploadForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm


class ProblemImportView(PermissionCheckMixin, GenericForm, FormView):
    required_permissions = [is_branch_admin]
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
            messages.error(self.request, str(e))
        return redirect("badmin:archive_import")


class ProblemPDFUploadView(PermissionCheckMixin, GenericForm, FormView):
    required_permissions = [is_country_admin]
    form_class = ProblemUploadForm
    form_title = "Upload problems"
    form_multipart = True
    require_unlocked_competition = False

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Successfully uploaded problems.")
        return redirect("badmin:archive_problem_upload")
