from collections import defaultdict

from bullet_admin.forms.teams import TeamForm
from bullet_admin.mixins import AnyAdminRequiredMixin, VenueMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from bullet_admin.views import DeleteView
from competitions.forms.registration import ContestantForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView
from education.models import School
from users.emails.teams import send_confirmation_email, send_deletion_email
from users.logic import get_school_symbol, get_venue_waiting_list
from users.models import Contestant, Team

from bullet import search
from bullet.views import FormAndFormsetMixin


class TeamListView(AnyAdminRequiredMixin, ListView):
    template_name = "bullet_admin/teams/list.html"
    paginate_by = 50

    def get_queryset(self):
        competition = get_active_competition(self.request)
        qs = Team.objects.filter(venue__category_competition__competition=competition)

        crole = self.request.user.get_competition_role(competition)
        if crole.countries:
            qs = qs.filter(venue__country__in=crole.countries)
        elif crole.venues:
            qs = qs.filter(venue__in=crole.venues)

        if self.request.GET.get("q"):
            ids = search.client.index("teams").search(
                self.request.GET["q"],
                {
                    "attributesToRetrieve": ["id"],
                    "filter": f"competition = {competition.id}",
                },
            )["hits"]
            ids = [x["id"] for x in ids]
            qs = qs.filter(id__in=ids)

        qs = (
            qs.select_related(
                "school",
                "venue",
                "venue__category_competition",
            )
            .prefetch_related("contestants", "contestants__grade")
            .order_by("id")
        )

        if self.request.GET.get("q"):
            qs = list(qs)
            qs.sort(key=lambda x: ids.index(x.id))

        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        brole = self.request.user.get_branch_role(self.request.BRANCH)
        crole = self.request.user.get_competition_role(
            get_active_competition(self.request)
        )
        ctx["hide_venue"] = (
            not brole.is_admin and not crole.countries and len(crole.venues) < 2
        )
        return ctx


class TeamToCompetitionView(AnyAdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, id=self.kwargs["pk"], is_waiting=True)
        if not can_access_venue(request, team.venue):
            return HttpResponseForbidden()

        team.to_competition()
        team.save()
        return HttpResponseRedirect(reverse("badmin:team_edit", kwargs={"pk": team.id}))


class TeamResendConfirmationView(AnyAdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, id=self.kwargs["pk"], confirmed_at__isnull=True)
        if not can_access_venue(request, team.venue):
            return HttpResponseForbidden()

        send_confirmation_email(team)
        messages.success(request, "The confirmation email was re-sent.")
        return HttpResponseRedirect(reverse("badmin:team_edit", kwargs={"pk": team.id}))


class WaitingListView(AnyAdminRequiredMixin, VenueMixin, ListView):
    template_name = "bullet_admin/teams/waiting.html"

    def get_queryset(self):
        return get_venue_waiting_list(self.venue)


class WaitingAutomoveView(AnyAdminRequiredMixin, VenueMixin, View):
    def post(self, request, *args, **kwargs):
        team_count = self.venue.remaining_capacity
        waiting_list = get_venue_waiting_list(self.venue)[:team_count]

        for team in waiting_list:
            team.to_competition()
            team.save()

        return HttpResponseRedirect(self.get_redirect_url())

    def get_redirect_url(self):
        url = reverse("badmin:waiting_list")
        if "venue" in self.request.GET:
            url += f"?venue={self.venue.id}"
        return url


class TeamEditView(AnyAdminRequiredMixin, FormAndFormsetMixin, UpdateView):
    template_name = "bullet_admin/teams/edit.html"
    form_class = TeamForm
    model = Team

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_access_venue(self.request, obj.venue):
            raise PermissionDenied()
        return obj

    def get_formset_class(self):
        return inlineformset_factory(
            Team, Contestant, form=ContestantForm, validate_max=True
        )

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_formset(self):
        fs = super().get_formset()
        team: Team = self.object
        fs.min_num = 0
        fs.max_num = team.venue.category_competition.max_members_per_team
        fs.extra = team.venue.category_competition.max_members_per_team
        return fs

    def get_formset_kwargs(self):
        kw = super().get_formset_kwargs()
        team: Team = self.object
        kw.update(
            {
                "form_kwargs": {
                    "school_types": team.school.types.prefetch_related("grades"),
                    "category": team.venue.category_competition,
                },
                "instance": team,
            }
        )
        return kw

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Team saved.")
        return reverse("badmin:team_list")


class TeamDeleteView(AnyAdminRequiredMixin, DeleteView):
    model = Team

    def post(self, request, *args, **kwargs):
        if not can_access_venue(request, self.get_object().venue):
            return HttpResponseForbidden()

        send_deletion_email(self.get_object())
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Team deleted.")
        return reverse("badmin:team_list")


class SchoolInputView(AnyAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        schools = []
        if "q" in request.GET:
            schools = search.client.index("schools").search(
                request.GET["q"],
                {"limit": 5},
            )["hits"]

        return TemplateResponse(
            request,
            "bullet_admin/partials/_school_input.html",
            {"schools": schools, "default": request.GET.get("default")},
        )

    def post(self, request, *args, **kwargs):
        school = get_object_or_404(School, id=request.POST.get("school"))
        return TemplateResponse(
            request,
            "bullet_admin/partials/_school_input_filled.html",
            {"school": school},
        )


class AssignTeamNumbersView(AnyAdminRequiredMixin, VenueMixin, TemplateView):
    template_name = "bullet_admin/teams/assign_numbers.html"

    def post(self, request, *args, **kwargs):
        last_number = Team.objects.filter(venue=self.venue).aggregate(Max("number"))[
            "number__max"
        ]
        if not last_number:
            last_number = 0

        teams = Team.objects.competing().filter(venue=self.venue)
        if "force" not in request.POST:
            teams = teams.filter(number__isnull=True)
        else:
            Team.objects.filter(venue=self.venue).update(
                number=None, in_school_symbol=None
            )

        # Assign team numbers
        for team in teams:
            last_number += 1
            team.number = last_number
            team.save()

        venue_teams = (
            Team.objects.competing().filter(venue=self.venue).order_by("number")
        )
        school_counts = defaultdict(lambda: 0)
        for team in venue_teams:
            school_counts[team.school_id] += 1

        symbol_counts = defaultdict(lambda: 0)
        for team in venue_teams:
            if school_counts[team.school_id] <= 1:
                if team.in_school_symbol:
                    team.in_school_symbol = None
                    team.save()
            else:
                symbol_counts[team.school_id] += 1
                team.in_school_symbol = get_school_symbol(symbol_counts[team.school_id])
                team.save()

        messages.success(request, "Numbers assigned successfully.")
        return HttpResponseRedirect(reverse("badmin:team_assign_numbers"))
