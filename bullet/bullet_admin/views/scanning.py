import json
from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from django_htmx.http import trigger_client_event
from problems.logic import (
    fix_results,
    get_last_problem_for_team,
    mark_problem_solved,
    mark_problem_unsolved,
)
from problems.logic.scanner import ScannedBarcode, parse_barcode, save_scan
from problems.models import Problem, ScannerLog, SolvedProblem
from users.models import Team
from users.models.organizers import User

from bullet_admin.access import PermissionCheckMixin, is_operator, is_operator_in
from bullet_admin.forms.review import get_review_formset
from bullet_admin.mixins import VenueMixin
from bullet_admin.utils import get_active_competition


class ProblemScanView(PermissionCheckMixin, View):
    required_permissions = [is_operator]

    def dispatch(self, request, *args, **kwargs):
        self.competition = get_active_competition(request)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        query = ScannerLog.objects.filter(
            user=self.request.user, timestamp__gte=timezone.now() - timedelta(days=5)
        ).order_by("-timestamp")
        paginator = Paginator(query, 15)
        page = paginator.get_page(self.request.GET.get("page", 1))
        return {
            "logs": page.object_list,
            "page_obj": page,
            "last_log": None,
            "scanned_code": None,
        }

    def get(self, request, *args, **kwargs):
        return TemplateResponse(
            request,
            "bullet_admin/scanning/problem.html",
            self.get_context_data(),
        )

    def scan(self, barcode) -> tuple[ScannerLog, ScannedBarcode | None]:
        user = self.request.user
        assert isinstance(user, User)
        ts = timezone.now()
        log = ScannerLog(timestamp=ts, user=user, barcode=barcode)
        try:
            scanned_barcode = parse_barcode(self.competition, barcode)
        except ValueError as e:
            log.result = ScannerLog.Result.SCAN_ERR
            log.message = str(e)
            log.save()
            return log, None

        if not is_operator_in(user, scanned_barcode.venue):
            log.result = ScannerLog.Result.SCAN_ERR
            log.message = (
                f"You don't have the required permissions to scan "
                f"problems in {scanned_barcode.venue.shortcode}."
            )
            log.save()
            return log, scanned_barcode

        if scanned_barcode.venue.start_time > timezone.now():
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = "The competition did not start yet."
            log.save()
            return log, scanned_barcode

        if scanned_barcode.venue.is_reviewed:
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = "The venue was already marked as reviewed."
            log.save()
            return log, scanned_barcode

        if scanned_barcode.team.is_reviewed:
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = "The team was already marked as reviewed."
            log.save()
            return log, scanned_barcode

        try:
            save_scan(scanned_barcode, ts)
        except ValueError as e:
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = str(e)
            log.save()
            return log, scanned_barcode

        log.result = ScannerLog.Result.OK
        log.save()
        return log, scanned_barcode

    def post(self, request, *args, **kwargs):
        barcode = self.request.POST.get("barcode", "").strip()[:32]
        if not barcode:
            return HttpResponse()

        log, barcode = self.scan(barcode)
        template = "bullet_admin/scanning/problem.html"
        if getattr(self.request, "htmx", False):
            template = "bullet_admin/scanning/problem/_response.html"

        ctx = self.get_context_data()
        ctx["last_log"] = log
        ctx["scanned_code"] = barcode
        response = TemplateResponse(request, template, ctx)
        return trigger_client_event(response, "scan-complete", {"result": log.result})


class VenueReviewView(PermissionCheckMixin, VenueMixin, TemplateView):
    required_permissions = [is_operator]
    template_name = "bullet_admin/scanning/review.html"

    def get_teams(self):
        return (
            Team.objects.competing()
            .filter(venue=self.venue, number__isnull=False)
            .select_related(
                "school",
                "venue",
            )
            .order_by("is_reviewed", "number")
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["teams"] = self.get_teams()
        return ctx

    def scan(self, request):
        start = self.venue.start_time
        end = start + self.venue.category.competition.competition_duration

        if timezone.now() < end:
            raise ValueError("The competition did not end yet.")

        scanned_barcode = parse_barcode(
            get_active_competition(request),
            request.POST.get("barcode"),
            allow_endmark=True,
        )

        if scanned_barcode.venue != self.venue:
            raise ValueError("The scanned team does not belong in the selected venue.")

        if scanned_barcode.team.is_reviewed:
            raise ValueError("The team was already reviewed.")

        max_problem_number = self.venue.category.competition.problem_count
        last = get_last_problem_for_team(scanned_barcode.team)
        if last < max_problem_number:
            if scanned_barcode.problem_number != last + 1:
                raise ValueError(
                    f"Expected problem number {last + 1}, got "
                    f"{scanned_barcode.problem_number}."
                )
        else:
            if scanned_barcode.problem_number != 0:
                raise ValueError(
                    f"Expected no more problems card, "
                    f"got {scanned_barcode.problem_number}."
                )

        scanned_barcode.team.is_reviewed = True
        scanned_barcode.team._change_reason = "reviewed via barcode"
        scanned_barcode.team.save()

    def post(self, request, *args, **kwargs):
        error = ""
        try:
            self.scan(request)
        except ValueError as e:
            error = e

        response = TemplateResponse(
            request,
            "bullet_admin/scanning/_review_teams_status.html",
            {
                "teams": self.get_teams(),
                "venue": self.venue,
                "error": error,
            },
        )
        return trigger_client_event(
            response, "scan-complete", {"result": 1 if error != "" else 0}
        )


class UndoScanView(PermissionCheckMixin, TemplateView):
    required_permissions = [is_operator]
    template_name = "bullet_admin/scanning/undo.html"

    def redirect(self, team: Team | None = None):
        if not team:
            return HttpResponseRedirect(reverse("badmin:scanning_problems"))
        return HttpResponseRedirect(
            f"{reverse('badmin:scanning_problems')}?venue={team.venue_id}"
        )

    def post(self, request, *args, **kwargs):
        user = request.user
        assert isinstance(user, User)
        try:
            scanned_barcode = parse_barcode(
                get_active_competition(request),
                request.GET.get("barcode", ""),
            )
        except ValueError as e:
            messages.error(request, str(e))
            return self.redirect()

        if not is_operator_in(user, scanned_barcode.venue):
            raise PermissionDenied()

        if scanned_barcode.team.is_reviewed:
            messages.error(request, "The team was already reviewed.")
            return self.redirect(scanned_barcode.team)

        mark_problem_unsolved(scanned_barcode.team, scanned_barcode.problem)

        ScannerLog.objects.create(
            user=user,
            barcode=f"*{request.GET.get('barcode')}",
            result=ScannerLog.Result.OK,
            message="Scan undone.",
            timestamp=timezone.now(),
        )
        messages.success(request, "The barcode scan was undone.")
        return self.redirect(scanned_barcode.team)


class TeamToggleReviewedView(PermissionCheckMixin, View):
    required_permissions = [is_operator]

    def post(self, request, *args, **kwargs):
        team: Team = get_object_or_404(Team, id=kwargs["pk"])

        if team.venue.is_reviewed:
            raise PermissionDenied()

        if not is_operator_in(request.user, team.venue):
            raise PermissionDenied()

        team.is_reviewed = not team.is_reviewed
        team._change_reason = "reviewed manually"
        team.save()

        return TemplateResponse(
            request,
            "bullet_admin/scanning/_review_teams.html",
            {
                "teams": Team.objects.competing()
                .filter(venue=team.venue, number__isnull=False)
                .order_by("is_reviewed", "number"),
                "venue": team.venue,
            },
        )


class TeamReviewView(PermissionCheckMixin, FormView):
    required_permissions = [is_operator_in]
    model = Team
    template_name = "bullet_admin/scanning/review_team.html"

    @cached_property
    def team(self) -> Team:
        return get_object_or_404(
            Team.objects.select_related("venue", "venue__category").prefetch_related(
                "solved_problems"
            ),
            pk=self.kwargs["pk"],
        )

    def get_permission_venue(self):
        return self.team.venue

    def check_custom_permission(self, user: User) -> bool | None:
        """The team and its venue cannot be reviewed."""
        return not self.team.is_reviewed and not self.team.venue.is_reviewed

    def get_form_class(self):
        return get_review_formset(self.team)

    def get_initial(self):  # type:ignore
        competition = get_active_competition(self.request)
        problems = Problem.objects.filter(competition=competition)

        solved_timestamps = {
            sp.problem_id: sp.competition_time for sp in self.team.solved_problems.all()
        }
        initial = []

        for problem in problems:
            if problem.number < self.team.venue.category.first_problem:
                continue

            row: dict[str, Any] = {"number": problem.number}
            if problem.id in solved_timestamps:
                row["is_solved"] = True
                row["competition_time"] = solved_timestamps[problem.id]

            initial.append(row)

        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = self.team
        return ctx

    def form_valid(self, form):
        competition = get_active_competition(self.request)
        problems: dict[int, Problem] = {
            p.number: p for p in Problem.objects.filter(competition=competition)
        }
        solved: dict[int, SolvedProblem] = {
            sp.problem_id: sp for sp in self.team.solved_problems.all()
        }

        changed = False
        for row in form:
            num = row.cleaned_data.get("number")
            if num not in problems or num < self.team.venue.category.first_problem:
                continue

            problem: Problem = problems[num]
            is_solved: bool = row.cleaned_data.get("is_solved")
            competition_time: timedelta = row.cleaned_data.get("competition_time")

            if problem.id in solved:
                old_solved = solved[problem.id]
                if not is_solved:
                    # Solved -> unsolved
                    mark_problem_unsolved(self.team, old_solved, repair_results=False)
                    changed = True
                else:
                    # Solved -> solved (changed time)
                    if competition_time != old_solved.competition_time:
                        mark_problem_unsolved(
                            self.team, old_solved, repair_results=False
                        )
                        mark_problem_solved(
                            self.team, problem, competition_time, repair_results=False
                        )
                        changed = True
            else:
                if is_solved:
                    # Unsolved -> solved
                    mark_problem_solved(
                        self.team, problem, competition_time, repair_results=False
                    )
                    changed = True

        if changed:
            fix_results(self.team)

        messages.success(self.request, "Team problems were updated.")
        return redirect("badmin:scanning_review_team", pk=self.team.id)


@method_decorator(csrf_exempt, name="dispatch")
class ApiProblemSolveView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.headers.get("X-API-KEY", "") != settings.PROBLEM_SOLVE_KEY:
            raise PermissionDenied()

        data = json.loads(request.body)

        for solve in data:
            team = Team.objects.filter(id=solve["team"]).first()
            if not team:
                continue
            problem = Problem.objects.filter(
                competition=team.venue.category.competition,
                number=solve["problem"],
            ).first()
            if not problem:
                continue
            timestamp = timezone.make_aware(datetime.fromtimestamp(solve["timestamp"]))

            if SolvedProblem.objects.filter(team=team, problem=problem).exists():
                continue

            mark_problem_solved(team, problem, timestamp)

        return HttpResponse("ok")
