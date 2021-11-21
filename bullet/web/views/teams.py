from competitions.models import CategoryCompetition, Competition, CompetitionSite
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import FormView, TemplateView
from users.models import Team
from web.forms import ParticipantsFormSet
from web.views import BranchViewMixin


class TeamEditView(BranchViewMixin, FormView):
    template_name = "web/team_edit.html"
    form_class = ParticipantsFormSet

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = self.team
        ctx["can_be_changed"] = self.can_be_changed
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Team successfully edited.")
        return redirect("team_edit", secret_link=self.team.secret_link)

    def get_form_kwargs(self):
        kw = super(TeamEditView, self).get_form_kwargs()
        kw["instance"] = self.team
        return kw

    def get_form(self, form_class=None):
        form = super(TeamEditView, self).get_form(form_class)
        category_competition: CategoryCompetition = (
            self.team.competition_site.category_competition
        )

        form.max_num = category_competition.max_members_per_team
        form.extra = category_competition.max_members_per_team - 1
        return form

    def dispatch(self, request, *args, **kwargs):
        self.team = (
            Team.objects.select_related("competition_site__category_competition")
            .prefetch_related("participants")
            .get(secret_link=kwargs.pop("secret_link"))
        )
        self.can_be_changed = (
            self.team.competition_site.category_competition.competition.competition_start
            > timezone.now()
        )

        return super(TeamEditView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.can_be_changed:
            raise PermissionDenied
        return super(TeamEditView, self).post(request, *args, **kwargs)


class TeamList(BranchViewMixin, TemplateView):
    template_name = "web/team_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        competition: Competition = Competition.objects.get_current_competition(
            self.branch
        )
        ctx["sites"] = (
            CompetitionSite.objects.filter(
                category_competition__competition=competition
            )
            .order_by("site__name")
            .all()
        )
        total_teams = 0
        for site in ctx["sites"]:
            total_teams += site.team_set.count()
        ctx["total_teams"] = total_teams
        ctx["countries"] = set(
            [site.site.address.locality.state.country for site in ctx["sites"]]
        )
        ctx["categories"] = CategoryCompetition.objects.filter(
            competition=competition
        ).all()
        return ctx
