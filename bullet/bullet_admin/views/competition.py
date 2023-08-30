from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.competition import CompetitionForm
from bullet_admin.views import GenericForm
from competitions.models import Competition
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView


class CompetitionFormMixin(GenericForm):
    form_class = CompetitionForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw


class CompetitionUpdateView(BranchAdminAccess, CompetitionFormMixin, UpdateView):
    form_title = "Edit competition"

    def get_object(self, queryset=None):
        return Competition.objects.get_current_competition(self.request.BRANCH)

    def form_valid(self, form):
        competition: Competition = form.save(commit=False)
        competition.branch = self.request.BRANCH
        competition.save()

        return redirect("badmin:competition_switch")


class CompetitionCreateView(BranchAdminAccess, CompetitionFormMixin, CreateView):
    form_title = "New competition"

    def form_valid(self, form):
        competition: Competition = form.save(commit=False)
        competition.branch = self.request.BRANCH
        competition.save()

        return redirect("badmin:competition_switch")
