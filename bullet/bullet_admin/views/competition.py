from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.competition import CompetitionForm
from bullet_admin.views import GenericForm
from competitions.models import Competition
from django.forms import Form
from django.shortcuts import redirect
from django.views.generic import CreateView, FormView, UpdateView
from problems.logic.stats import generate_stats


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
        return Competition.objects.get_current_competition(self.request.BRANCH)

    def form_valid(self, form):
        competition: Competition = form.save(commit=False)
        competition.branch = self.request.BRANCH

        if "finalize" in self.request.POST:
            return redirect("badmin:competition_confirm")

        competition.save()

        return redirect("badmin:competition_switch")


class CompetitionCreateView(BranchAdminAccess, CompetitionFormMixin, CreateView):
    form_title = "New competition"

    def form_valid(self, form):
        competition: Competition = form.save(commit=False)
        competition.branch = self.request.BRANCH
        competition.save()

        return redirect("badmin:competition_switch")


class CompetitionFinalizeConfirmView(BranchAdminAccess, FormView):
    form_title = "Really finalize current competition?"
    form_class = Form
    template_name = "bullet_admin/competition/confirm.html"

    def form_valid(self, form):
        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        if "finalize" in self.request.POST:
            self.finalize(competition)

        return redirect("badmin:competition_switch")

    @staticmethod
    def finalize(competition: "Competition"):
        competition.results_public = True
        generate_stats(competition)

        competition.save()
