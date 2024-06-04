import csv
import json
from collections import defaultdict
from datetime import datetime
from functools import partial

import yaml
from competitions.forms.registration import ContestantForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from documents.models import TexJob
from education.models import Grade, School
from users.emails.teams import (
    send_confirmation_email,
    send_deletion_email,
    send_to_competition_email,
)
from users.logic import get_school_symbol
from users.models import Contestant, Team

from bullet import search
from bullet.views import FormAndFormsetMixin
from bullet_admin.access import AdminAccess
from bullet_admin.forms.teams import TeamExportForm, TeamFilterForm, TeamForm
from bullet_admin.forms.tex import TexTeamRenderForm
from bullet_admin.mixins import (
    AdminRequiredMixin,
    IsOperatorContext,
    OperatorRequiredMixin,
    RedirectBackMixin,
    VenueMixin,
)
from bullet_admin.utils import can_access_venue, get_active_competition
from bullet_admin.views import GenericForm


class TeamListView(OperatorRequiredMixin, IsOperatorContext, ListView):
    template_name = "bullet_admin/teams/list.html"
    paginate_by = 100

    def get_form(self):
        return TeamFilterForm(
            get_active_competition(self.request),
            self.request.user,
            data=self.request.GET,
        )

    def get_queryset(self):
        competition = get_active_competition(self.request)
        qs = Team.objects.filter(venue__category__competition=competition)

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
                "venue__category",
                "spanish_data",
            )
            .prefetch_related("contestants", "contestants__grade")
            .order_by("venue__name", "venue__category__identifier", "number", "id")
        )

        qs = self.get_form().apply_filter(qs)

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
        ctx["search_form"] = self.get_form()
        return ctx


class TeamExportView(AdminRequiredMixin, FormView):
    template_name = "bullet_admin/teams/export.html"
    form_class = TeamExportForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        competition = get_active_competition(self.request)
        qs = (
            Team.objects.filter(venue__category__competition=competition)
            .select_related(
                "school",
                "venue",
                "venue__category",
            )
            .prefetch_related("contestants", "contestants__grade")
            .order_by("venue__name", "venue__category__identifier", "number", "id")
            .annotate(solved_problem_count=Count("solved_problems__id"))
        )
        qs = form.apply_filter(qs)

        data = [
            team.to_export(form.cleaned_data["format"] == TeamExportForm.Format.CSV)
            for team in qs
        ]

        response = None
        if form.cleaned_data["format"] == TeamExportForm.Format.JSON:
            response = HttpResponse(content_type="application/json")
            json.dump(data, response)
        elif form.cleaned_data["format"] == TeamExportForm.Format.CSV:
            response = HttpResponse(content_type="text/csv")
            w = csv.DictWriter(response, data[0].keys() if len(data) > 0 else [])
            w.writeheader()
            w.writerows(data)
        elif form.cleaned_data["format"] == TeamExportForm.Format.YAML:
            response = HttpResponse(content_type="text/yaml")
            yaml.dump(data, response)

        return response


class TeamToCompetitionView(AdminRequiredMixin, RedirectBackMixin, TemplateView):
    model = Team
    template_name = "bullet_admin/teams/to_competition.html"

    def get_default_success_url(self):
        return reverse("badmin:team_edit", kwargs={"pk": self.kwargs["pk"]})

    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, id=self.kwargs["pk"], is_waiting=True)
        if not can_access_venue(request, team.venue):
            return HttpResponseForbidden()

        team.to_competition()
        team.save()

        send_to_competition_email.delay(team.id)
        return HttpResponseRedirect(self.get_success_url())


class TeamGenerateDocumentView(AdminAccess, GenericForm, FormView):
    require_unlocked_competition = False
    form_class = TexTeamRenderForm
    form_title = "Generate TeX Document"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        team = get_object_or_404(Team, id=self.kwargs["pk"]).to_export()
        job = TexJob.objects.create(
            creator=self.request.user,
            template=form.cleaned_data["template"],
            context={"teams": [team], "team": team},
        )
        job.render()

        return redirect("badmin:tex_job_detail", pk=job.id)


class TeamResendConfirmationView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, id=self.kwargs["pk"], confirmed_at__isnull=True)
        if not can_access_venue(request, team.venue):
            return HttpResponseForbidden()

        send_confirmation_email.delay(team.id)
        messages.success(request, "The confirmation email was re-sent.")
        return HttpResponseRedirect(reverse("badmin:team_edit", kwargs={"pk": team.id}))


class TeamEditView(
    OperatorRequiredMixin,
    IsOperatorContext,
    RedirectBackMixin,
    FormAndFormsetMixin,
    UpdateView,
):
    template_name = "bullet_admin/teams/edit.html"
    model = Team

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_access_venue(self.request, obj.venue):
            raise PermissionDenied()
        return obj

    def get_form_class(self):
        competition = get_active_competition(self.request)
        crole = self.request.user.get_competition_role(competition)

        venue = self.object.venue
        if crole.is_operator:
            return venue.registration_flow.get_operator_form()
        return venue.registration_flow.get_admin_form()

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
        fs.max_num = team.venue.category.max_members_per_team
        fs.extra = team.venue.category.max_members_per_team
        return fs

    def get_formset_kwargs(self):
        kw = super().get_formset_kwargs()
        team: Team = self.object
        kw.update(
            {
                "form_kwargs": {
                    "school_types": team.school.types.prefetch_related("grades"),
                    "category": team.venue.category,
                },
                "instance": team,
            }
        )
        return kw

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def save_forms(self, form, formset):
        obj = form.save(commit=False)
        if "venue" in form.changed_data:
            obj.number = None
            obj.in_school_symbol = None
        if "school" in form.changed_data:
            obj.in_school_symbol = None
        obj.save()
        formset.save()
        messages.success(self.request, "Team saved.")

    def get_default_success_url(self):
        return reverse("badmin:team_list")


class TeamDeleteView(AdminRequiredMixin, DeleteView):
    model = Team
    template_name = "bullet_admin/teams/delete.html"

    def post(self, request, *args, **kwargs):
        send_mail = "send_mail" in self.request.POST
        obj = self.get_object()
        if not can_access_venue(request, obj.venue):
            return HttpResponseForbidden()

        if send_mail:
            send_deletion_email.delay(obj)
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Team deleted.")
        return reverse("badmin:team_list")


class SchoolInputView(AdminRequiredMixin, View):
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


class AssignTeamNumbersView(AdminRequiredMixin, VenueMixin, TemplateView):
    template_name = "bullet_admin/teams/assign_numbers.html"

    @transaction.atomic
    def assign_numbers(self, force):
        teams = Team.objects.competing().filter(venue=self.venue).order_by("?")
        ideal_numbers = set(range(1, teams.count() + 1))
        if not force:
            used_numbers = set(teams.values_list("number", flat=True))
            ideal_numbers.difference_update(used_numbers)
        ideal_numbers = sorted(list(ideal_numbers), reverse=True)

        if force:
            teams.update(number=None)

        for team in teams:
            if team.number is None:
                team.number = ideal_numbers.pop()
                team.save()

    @transaction.atomic
    def assign_symbols(self, force):
        teams = Team.objects.competing().filter(venue=self.venue).order_by("?")
        school_symbols = defaultdict(lambda: set())  # sets of used symbols
        school_counts = defaultdict(lambda: 0)  # counts of teams from school

        for team in teams:
            if team.in_school_symbol:
                school_symbols[team.school_id].add(team.in_school_symbol)
            school_counts[team.school_id] += 1

        school_unused_symbols = {}
        for school in school_counts.keys():
            if school_counts[school] == 1:
                continue

            symbols = set(
                [get_school_symbol(i) for i in range(1, school_counts[school] + 1)]
            )
            if not force:
                symbols.difference_update(school_symbols[school])
            school_unused_symbols[school] = sorted(list(symbols), reverse=True)

        if force:
            teams.update(in_school_symbol=None)

        for team in teams:
            # the team should not have a symbol
            if school_counts[team.school_id] == 1 and team.in_school_symbol:
                team.in_school_symbol = None
                team.save()

            # the team should have a symbol
            if school_counts[team.school_id] > 1 and not team.in_school_symbol:
                team.in_school_symbol = school_unused_symbols[team.school_id].pop()
                team.save()

    @transaction.atomic
    def assign_passwords(self):
        teams = Team.objects.competing().filter(venue=self.venue).order_by("id")
        for team in teams:
            if not team.online_password:
                team.generate_online_password()
                team.save()

    def post(self, request, *args, **kwargs):
        force = "force" in request.POST
        self.assign_numbers(force)
        self.assign_symbols(force)

        if self.venue.is_online:
            self.assign_passwords()

        messages.success(request, "Numbers assigned successfully.")
        u = reverse("badmin:team_assign_numbers")
        return HttpResponseRedirect(f"{u}?venue={self.venue.id}")


class TeamCreateView(AdminAccess, CreateView):
    template_name = "bullet_admin/teams/create.html"

    def get_form_class(self):
        competition = get_active_competition(self.request)
        crole = self.request.user.get_competition_role(competition)

        if crole.is_operator:
            return HttpResponseForbidden()
        return TeamForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["instance"] = None
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        send_mail = "send_mail" in self.request.POST
        team = form.save(commit=False)
        if not send_mail:
            team.confirmed_at = datetime.now()
        team.save()
        messages.success(self.request, "Team saved.")
        if send_mail:
            transaction.on_commit(partial(send_confirmation_email.delay, team.id))
        return HttpResponseRedirect(reverse("badmin:team_list"))


def get_team_members(team, time):
    return Contestant.history.as_of(time).filter(team=team)


class TeamHistoryView(AdminAccess, ListView):
    model = Team
    template_name = "bullet_admin/teams/history.html"

    def get_queryset(self, *args, **kwargs):
        qs = []
        team = Team.objects.get(id=self.kwargs["pk"])
        current = team.history.first()

        prev_members = get_team_members(team, datetime.now())
        t = datetime.now()
        while current.prev_record:
            current_members, prev_members = (
                prev_members,
                get_team_members(team, current.history_date),
            )
            members_changes = []
            for member in current_members:
                if member in prev_members:
                    cur_member = member.history.filter(history_date__lte=t).first()
                    prev_member = member.history.filter(
                        history_date__lte=current.history_date
                    ).first()

                    changes = cur_member.diff_against(prev_member).changes
                    if changes:
                        for change in changes:
                            if change.field == "grade":
                                change.old = Grade.objects.get(id=change.old)
                                change.new = Grade.objects.get(id=change.new)
                        members_changes.append({"member": member, "changes": changes})

            changes = current.diff_against(current.prev_record).changes
            qs.append(
                {
                    "user": current.history_user,
                    "time": current.history_date,
                    "changes": changes,
                    "added_members": [
                        member
                        for member in current_members
                        if member not in prev_members
                    ],
                    "removed_members": [
                        member
                        for member in prev_members
                        if member not in current_members
                    ],
                    "members_changes": members_changes,
                }
            )
            t = current.history_date
            current = current.prev_record
        return qs
