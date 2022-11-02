from bullet_admin.mixins import OperatorRequiredMixin, VenueMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from problems.logic import get_last_problem_for_team
from problems.logic.scanner import parse_barcode, save_scan
from problems.models import ScannerLog
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
        barcode = self.request.POST.get("barcode", "").strip()
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
            get_active_competition(request), request.POST.get("barcode")
        )

        if scanned_barcode.venue != self.venue:
            raise ValueError("The scanned team does not belong in the selected venue.")

        if scanned_barcode.team.is_reviewed:
            raise ValueError("The team was already reviewed.")

        last = get_last_problem_for_team(scanned_barcode.team)
        if scanned_barcode.problem_number != last + 1:
            raise ValueError(
                f"Expected problem number {last + 1}, got "
                f"{scanned_barcode.problem_number}."
            )

        scanned_barcode.team.is_reviewed = True
        scanned_barcode.team.save()

        if not Team.objects.filter(venue=self.venue, is_reviewed=False).exists():
            self.venue.is_reviewed = True
            self.venue.save()

    def post(self, request, *args, **kwargs):
        error = ""
        try:
            self.scan(request)
        except ValueError as e:
            error = e

        return TemplateResponse(
            request,
            "bullet_admin/scanning/_review_teams_status.html",
            {
                "teams": self.get_teams(),
                "error": error,
            },
        )
