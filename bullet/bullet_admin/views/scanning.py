from bullet_admin.mixins import AnyAdminRequiredMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views import View
from problems.models import ScannerLog
from problems.scanner import parse_barcode, save_scan


class ProblemScanView(AnyAdminRequiredMixin, View):
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

        # TODO: Check competition start + review end

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
