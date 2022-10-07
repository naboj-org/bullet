from bullet_admin.forms.teams import TeamForm
from bullet_admin.mixins import AnyAdminRequiredMixin, VenueMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from competitions.forms.registration import ContestantForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, UpdateView
from education.models import School
from users.emails.teams import send_confirmation_email
from users.logic import get_venue_waiting_list
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
        if crole.country:
            qs = qs.filter(venue__country=crole.country)
        elif crole.venue:
            qs = qs.filter(venue=crole.venue)

        if "q" in self.request.GET:
            ids = search.client.index("teams").search(
                self.request.GET["q"], {"attributesToRetrieve": ["id"]}
            )["hits"]
            ids = [x["id"] for x in ids]
            qs = qs.filter(id__in=ids)

        return (
            qs.select_related(
                "school",
                "venue",
                "venue__category_competition",
            )
            .prefetch_related("contestants", "contestants__grade")
            .order_by("id")
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["hide_venue"] = (
            self.request.user.get_competition_role(
                get_active_competition(self.request)
            ).venue
            is not None
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


class SchoolInputView(AnyAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        schools = []
        if "q" in request.GET:
            schools = search.client.index("schools").search(
                request.GET["q"],
                {"limit": 5},
            )["hits"]

        return TemplateResponse(
            request, "bullet_admin/partials/_school_input.html", {"schools": schools}
        )

    def post(self, request, *args, **kwargs):
        school = get_object_or_404(School, id=request.POST.get("school"))
        return TemplateResponse(
            request,
            "bullet_admin/partials/_school_input_filled.html",
            {"school": school},
        )
