from competitions.models import Competition
from django.contrib import messages
from django.forms import Form
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, FormView, UpdateView
from problems.logic.results import save_all_ranks, squash_results
from problems.logic.stats import generate_stats
from users.logic import move_all_eligible_teams

from bullet_admin.access import BranchAdminAccess, UnlockedCompetitionMixin
from bullet_admin.forms.competition import CompetitionForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm


class CompetitionFormMixin(GenericForm):
    form_class = CompetitionForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw


class CompetitionUpdateView(BranchAdminAccess, CompetitionFormMixin, UpdateView):
    form_title = "Edit competition"
    template_name = "bullet_admin/competition/form.html"

    def get_object(self, queryset=None):
        return get_active_competition(self.request)

    def get_success_url(self):
        return reverse("badmin:competition_switch")


class CompetitionCreateView(BranchAdminAccess, CompetitionFormMixin, CreateView):
    form_title = "New competition"

    def form_valid(self, form):
        competition: Competition = form.save(commit=False)
        competition.branch = self.request.BRANCH
        competition.save()

        return redirect("badmin:competition_switch")


class CompetitionFinalizeView(UnlockedCompetitionMixin, BranchAdminAccess, FormView):
    form_class = Form
    template_name = "bullet_admin/competition/confirm.html"

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


class CompetitionAutomoveView(
    UnlockedCompetitionMixin, BranchAdminAccess, GenericForm, FormView
):
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
