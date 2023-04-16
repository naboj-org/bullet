import json
from datetime import datetime, timedelta

from bullet_admin.forms.review import get_review_formset
from bullet_admin.mixins import OperatorRequiredMixin, VenueMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from problems.logic import (
    fix_results,
    get_last_problem_for_team,
    mark_problem_solved,
    mark_problem_unsolved,
)
from problems.logic.scanner import parse_barcode, save_scan
from problems.models import CategoryProblem, Problem, ScannerLog, SolvedProblem
from users.models import Team


class ProblemScanView(OperatorRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.competition = get_active_competition(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return TemplateResponse(
            request,
            "bullet_admin/scanning/problem.html",
            {
                "logs": ScannerLog.objects.filter(user=self.request.user).order_by(
                    "-timestamp"
                )
            },
        )

    def scan(self, barcode) -> ScannerLog:
        ts = timezone.now()
        log = ScannerLog(timestamp=ts, user=self.request.user, barcode=barcode)
        try:
            scanned_barcode = parse_barcode(self.competition, barcode)
        except ValueError as e:
            log.result = ScannerLog.Result.SCAN_ERR
            log.message = str(e)
            log.save()
            return log

        if not can_access_venue(self.request, scanned_barcode.venue):
            log.result = ScannerLog.Result.SCAN_ERR
            log.message = (
                f"You don't have the required permissions to scan "
                f"problems in {scanned_barcode.venue.shortcode}."
            )
            log.save()
            return log

        if scanned_barcode.venue.start_time > timezone.now():
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = "The competition did not start yet."
            log.save()
            return log

        if scanned_barcode.venue.is_reviewed:
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = "The venue was already marked as reviewed."
            log.save()
            return log

        if scanned_barcode.team.is_reviewed:
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = "The team was already marked as reviewed."
            log.save()
            return log

        try:
            save_scan(scanned_barcode, ts)
        except ValueError as e:
            log.result = ScannerLog.Result.INTEGRITY_ERR
            log.message = str(e)
            log.save()
            return log

        log.result = ScannerLog.Result.OK
        log.save()
        return log

    def post(self, request, *args, **kwargs):
        barcode = self.request.POST.get("barcode", "").strip()[:32]
        if not barcode:
            return HttpResponse()

        log = self.scan(barcode)
        return TemplateResponse(
            request, "bullet_admin/scanning/_logentry.html", {"log": log}
        )


class VenueReviewView(OperatorRequiredMixin, VenueMixin, TemplateView):
    template_name = "bullet_admin/scanning/review.html"

    def get_teams(self):
        return (
            Team.objects.competing()
            .filter(venue=self.venue, number__isnull=False)
            .order_by("is_reviewed", "number")
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["teams"] = self.get_teams()
        return ctx

    def scan(self, request):
        start = self.venue.start_time
        end = start + self.venue.category_competition.competition.competition_duration

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

        problem_count = CategoryProblem.objects.filter(
            category=scanned_barcode.team.venue.category_competition
        ).count()
        last = get_last_problem_for_team(scanned_barcode.team)
        if last < problem_count:
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
        scanned_barcode.team.save()

        if (
            not Team.objects.competing()
            .filter(venue=self.venue, is_reviewed=False)
            .exists()
        ):
            self.venue.is_reviewed = True
            self.venue.save()

    def post(self, request, *args, **kwargs):
        error = ""
        try:
            self.scan(request)
        except ValueError as e:
            error = e

        # TODO: Replace with self.render_to_response()
        return TemplateResponse(
            request,
            "bullet_admin/scanning/_review_teams_status.html",
            {
                "teams": self.get_teams(),
                "venue": self.venue,
                "error": error,
            },
        )


class TeamToggleReviewedView(OperatorRequiredMixin, VenueMixin, View):
    def post(self, request, *args, **kwargs):
        team: Team = get_object_or_404(Team, id=kwargs["pk"])

        if team.venue.is_reviewed:
            raise PermissionDenied()

        if not can_access_venue(request, team.venue):
            raise PermissionDenied()

        team.is_reviewed = not team.is_reviewed
        team._change_reason = "Manual review"
        team.save()

        if (
            not Team.objects.competing()
            .filter(venue=team.venue, is_reviewed=False)
            .exists()
        ):
            team.venue.is_reviewed = True
            team.venue.save()

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


class TeamReviewView(OperatorRequiredMixin, FormView):
    model = Team
    template_name = "bullet_admin/scanning/review_team.html"

    def dispatch(self, request, *args, **kwargs):
        self.team: Team = (
            Team.objects.select_related("venue", "venue__category_competition")
            .prefetch_related("solved_problems")
            .get(pk=kwargs["pk"])
        )
        if not can_access_venue(request, self.team.venue):
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_review_formset(self.team)

    def get_initial(self):
        category_problems = {
            cp.number: cp.problem_id
            for cp in CategoryProblem.objects.filter(
                category=self.team.venue.category_competition
            ).order_by("number")
        }
        solved_timestamps = {
            sp.problem_id: sp.competition_time for sp in self.team.solved_problems.all()
        }
        initial = []

        for num, id in category_problems.items():
            row = {"number": num}
            if id in solved_timestamps:
                row["is_solved"] = True
                row["competition_time"] = solved_timestamps[id]

            initial.append(row)

        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = self.team
        return ctx

    def form_valid(self, form):
        category_problems: dict[int, Problem] = {
            cp.number: cp.problem
            for cp in CategoryProblem.objects.filter(
                category=self.team.venue.category_competition
            )
            .order_by("number")
            .select_related("problem")
        }
        solved: dict[int, SolvedProblem] = {
            sp.problem_id: sp for sp in self.team.solved_problems.all()
        }

        changed = False
        for row in form:
            num = row.cleaned_data.get("number")
            if num not in category_problems:
                continue
            problem: Problem = category_problems[num]
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
                competition=team.venue.category_competition.competition,
                category_problems__category=team.venue.category_competition,
                category_problems__number=solve["problem"],
            ).first()
            if not problem:
                continue
            timestamp = timezone.make_aware(datetime.fromtimestamp(solve["timestamp"]))

            if SolvedProblem.objects.filter(team=team, problem=problem).exists():
                continue

            mark_problem_solved(team, problem, timestamp)

        return HttpResponse("ok")
