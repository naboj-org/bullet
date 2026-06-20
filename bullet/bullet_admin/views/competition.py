import os.path
import zipfile

from competitions.models import Competition
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, FormView, UpdateView
from problems.logic.results import save_all_ranks, squash_results
from problems.logic.stats import generate_stats
from users.logic import move_all_eligible_teams

from bullet_admin.access import (
    PermissionCheckMixin,
    is_branch_admin,
    is_competition_unlocked,
    is_country_admin,
)
from bullet_admin.forms.competition import CompetitionForm, TearoffUploadForm
from bullet_admin.utils import get_active_branch, get_active_competition, sendfile
from bullet_admin.views import GenericForm


class CompetitionUpdateView(PermissionCheckMixin, GenericForm, UpdateView):
    required_permissions = [is_branch_admin]
    form_class = CompetitionForm
    form_title = "Edit competition"
    template_name = "bullet_admin/competition/form.html"

    def get_object(self, queryset=None):
        return get_active_competition(self.request)

    def get_success_url(self):
        return reverse("badmin:competition_switch")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["branch"] = get_active_branch(self.request)
        return kwargs


class CompetitionCreateView(PermissionCheckMixin, GenericForm, CreateView):
    required_permissions = [is_branch_admin]
    form_class = CompetitionForm
    form_title = "New competition"

    def get_success_url(self):
        return reverse("badmin:competition_switch")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["branch"] = get_active_branch(self.request)
        return kwargs


class CompetitionFinalizeView(PermissionCheckMixin, GenericForm, FormView):
    required_permissions = [is_branch_admin, is_competition_unlocked]
    form_class = Form
    form_title = "Finalize competition?"
    form_submit_label = "Finalize"
    form_submit_color = "red"
    form_submit_icon = "mdi:check"
    template_name = "bullet_admin/competition/finalize.html"

    def form_valid(self, form):
        competition = get_active_competition(self.request)
        self.finalize(competition)
        messages.success(self.request, "The competition was finalized.")
        return redirect("badmin:competition_switch")

    @staticmethod
    def finalize(competition: "Competition"):
        competition.results_public = True
        generate_stats.delay(competition.id)
        squash_results.delay(competition.id)
        save_all_ranks.delay(competition.id)
        competition.save()


class CompetitionAutomoveView(PermissionCheckMixin, GenericForm, FormView):
    required_permissions = [is_branch_admin, is_competition_unlocked]
    form_class = Form
    form_title = "Move waiting lists automatically"
    form_submit_label = "Move automatically"
    form_submit_color = "green"
    form_submit_icon = "mdi:fast-forward"
    template_name = "bullet_admin/competition/automove.html"

    def form_valid(self, form):
        competition = get_active_competition(self.request)
        move_all_eligible_teams.delay(competition.id)
        messages.success(
            self.request, "The teams will be moved to the competition shortly."
        )
        return redirect("badmin:home")


class CompetitionTearoffUploadFileView(PermissionCheckMixin, View):
    def get(self, request, *args, **kwargs):
        tearoff_filename = self.kwargs["tearoff_filename"]

        if not tearoff_filename.lower().endswith(".pdf"):
            return HttpResponse("Not a PDF.", status=400)

        competition = get_active_competition(request)
        file_path = competition.secret_dir / "tearoffs" / tearoff_filename

        if not default_storage.exists(file_path):
            return HttpResponse(f"File '{tearoff_filename}' not found", status=404)

        return sendfile(default_storage.path(file_path), as_attachment=True)


class CompetitionTearoffUploadView(PermissionCheckMixin, GenericForm, FormView):
    required_permissions = [is_country_admin, is_competition_unlocked]
    form_class = TearoffUploadForm
    form_title = "Tearoff upload"
    form_multipart = True
    template_name = "bullet_admin/competition/tearoff.html"

    def get_upload_folder(self):
        competition = get_active_competition(self.request)
        return str(competition.secret_dir / "tearoffs")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        path = self.get_upload_folder()
        if not default_storage.exists(path):
            files = []
        else:
            files = default_storage.listdir(path)[1]

        ctx["available_files"] = [
            {
                "name": file,
                "modified_time": default_storage.get_modified_time(
                    os.path.join(path, file)
                ),
            }
            for file in sorted(files)
        ]
        return ctx

    def is_valid_name(self, name):
        return name in {code for code, _ in settings.LANGUAGES}

    def upload_zip(self, problems):
        target_dir = default_storage.path(self.get_upload_folder())
        invalid_files = []
        uploaded_files = []

        with zipfile.ZipFile(problems) as zipf:
            for file in zipf.namelist():
                name, extension = os.path.splitext(file)
                if extension.lower() != ".pdf":
                    continue

                if not self.is_valid_name(name):
                    invalid_files.append(file)
                    continue

                zipf.extract(file, target_dir)
                uploaded_files.append(file)

        return invalid_files, uploaded_files

    def upload_pdf(self, problems):
        name, _ = os.path.splitext(problems.name)
        if not self.is_valid_name(name):
            return [problems.name], []
        path = os.path.join(self.get_upload_folder(), problems.name)
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, problems)
        return [], [problems.name]

    def form_valid(self, form):
        problems = form.cleaned_data["problems"]

        if problems.name.lower().endswith(".zip"):
            invalid_files, uploaded_files = self.upload_zip(problems)
        else:
            invalid_files, uploaded_files = self.upload_pdf(problems)

        if invalid_files:
            messages.error(
                self.request,
                "Invalid tearoff file names: " + ", ".join(invalid_files),
            )
        if uploaded_files:
            messages.success(self.request, "Tearoffs uploaded successfully.")
        return redirect("badmin:competition_upload_tearoffs")
