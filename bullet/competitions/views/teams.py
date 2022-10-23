from collections import defaultdict

from competitions.forms.registration import ContestantForm
from competitions.models import CategoryCompetition, Competition, Venue
from countries.models import BranchCountry
from countries.utils import country_reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import inlineformset_factory
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, FormView, TemplateView
from users.logic import (
    add_team_to_competition,
    get_venue_waiting_list,
    get_venues_waiting_list,
)
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
        messages.success(self.request, _("Team successfully edited."))
        return HttpResponseRedirect(
            country_reverse("team_edit", kwargs={"secret_link": self.team.secret_link})
        )

    def get_form_kwargs(self):
        kw = super(TeamEditView, self).get_form_kwargs()
        kw["instance"] = self.team
        kw["form_kwargs"] = {
            "school_types": self.team.school.types.prefetch_related("grades"),
            "category": self.category_competition,
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
            .filter(secret_link=kwargs.pop("secret_link"))
            .first()
        )
        if not self.team:
            raise Http404()

        self.category_competition = self.team.venue.category_competition
        self.can_be_changed = (
            self.category_competition.competition.competition_start > timezone.now()
            and not self.team.is_checked_in
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

    def get_teams(self, venues) -> QuerySet[Team]:
        return Team.objects.competing().filter(venue__in=venues)

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
            .order_by("name", "category_competition__identifier")
            .select_related("category_competition")
            .all()
        )
        teams: QuerySet[Team] = (
            self.get_teams(venues)
            .prefetch_related("contestants", "contestants__grade")
            .select_related("school")
            .all()
        )

        venue_teams: dict[int, list[Team]] = defaultdict(lambda: [])
        for team in teams:
            venue_teams[team.venue_id].append(team)

        ctx["venues"] = [{"venue": v, "teams": venue_teams[v.id]} for v in venues]
        ctx["country"] = country
        ctx["countries"] = (
            BranchCountry.objects.filter(branch=self.request.BRANCH)
            .order_by("country")
            .all()
        )
        return ctx


class WaitingListView(TeamListView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_waitinglist"] = True
        return ctx

    def get_teams(self, venues) -> QuerySet[Team]:
        return get_venues_waiting_list(venues)


class TeamDeleteView(DeleteView):
    template_name = "teams/delete.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Team, secret_link=self.kwargs["secret_link"])

    def form_valid(self, form):
        team: Team = self.object
        category: CategoryCompetition = team.venue.category_competition
        competition: Competition = category.competition
        if team.is_checked_in or competition.competition_start <= timezone.now():
            return HttpResponseForbidden()

        self.object.delete()
        messages.success(self.request, _("Team was unregistered."))

        if competition.is_registration_open and not team.is_waiting:
            waiting_list = get_venue_waiting_list(team.venue).first()
            if (
                waiting_list
                and waiting_list.from_school
                <= category.max_teams_per_school_at(timezone.now())
            ):
                waiting_list.to_competition()
                waiting_list.save()

        # TODO: notify admins
        return HttpResponseRedirect(country_reverse("homepage"))
