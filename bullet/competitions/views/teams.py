from collections import defaultdict

from competitions.forms.registration import ContestantForm
from competitions.models import Competition, Venue
from countries.models import BranchCountry
from countries.utils import country_reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, FormView, TemplateView
from users.logic import add_team_to_competition
from users.models import Contestant, Team


class TeamEditView(FormView):
    template_name = "teams/edit.html"

    def get_form_class(self):
        return inlineformset_factory(
            Team, Contestant, form=ContestantForm, validate_max=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = self.team
        ctx["can_be_changed"] = self.can_be_changed
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Team successfully edited.")
        return HttpResponseRedirect(
            country_reverse("team_edit", kwargs={"secret_link": self.team.secret_link})
        )

    def get_form_kwargs(self):
        kw = super(TeamEditView, self).get_form_kwargs()
        kw["instance"] = self.team
        kw["form_kwargs"] = {
            "school_types": self.team.school.types.prefetch_related("grades"),
        }
        return kw

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.min_num = 0
        form.max_num = self.category_competition.max_members_per_team
        form.extra = self.category_competition.max_members_per_team
        return form

    def dispatch(self, request, *args, **kwargs):
        self.team = (
            Team.objects.select_related("venue__category_competition")
            .prefetch_related("contestants")
            .get(secret_link=kwargs.pop("secret_link"))
        )
        self.category_competition = self.team.venue.category_competition
        self.can_be_changed = (
            self.category_competition.competition.competition_start > timezone.now()
        )

        if self.team.confirmed_at is None:
            self.team.confirmed_at = timezone.now()
            add_team_to_competition(self.team)
            self.team.save()
            messages.success(request, _("Registration successfully confirmed."))

        return super(TeamEditView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.can_be_changed:
            raise PermissionDenied
        return super(TeamEditView, self).post(request, *args, **kwargs)


class TeamListView(TemplateView):
    template_name = "teams/list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        competition: Competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )

        country: str = self.request.GET.get(
            "country", self.request.COUNTRY_CODE
        ).upper()
        venues: QuerySet[Venue] = (
            Venue.objects.filter(
                category_competition__competition=competition, country=country
            )
            .order_by("name")
            .select_related("category_competition")
            .all()
        )
        teams: QuerySet[Team] = (
            Team.objects.filter(venue__in=venues)
            .prefetch_related("contestants", "contestants__grade")
            .select_related("school")
            .all()
        )  # TODO: show only competing teams

        venue_teams: dict[int, list[Team]] = defaultdict(lambda: [])
        for team in teams:
            venue_teams[team.venue_id].append(team)

        ctx["venues"] = [{"venue": v, "teams": venue_teams[v.id]} for v in venues]
        ctx["sites"] = venues
        ctx["country"] = country
        ctx["countries"] = (
            BranchCountry.objects.filter(branch=self.request.BRANCH)
            .order_by("country")
            .all()
        )
        return ctx


class TeamDeleteView(DeleteView):
    template_name = "teams/delete.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Team, secret_link=self.kwargs["secret_link"])

    def form_valid(self, form):
        self.object.delete()
        messages.success(self.request, _("Team was unregistered."))
        # TODO: notify admins
        return HttpResponseRedirect(country_reverse("homepage"))
