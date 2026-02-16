from competitions.models import Venue
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView

from bullet_admin.utils import get_active_competition


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "bullet_admin/home/main.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["competition"] = get_active_competition(self.request)
        ctx["venues"] = (
            Venue.objects.for_request(self.request)
            .annotate(
                waiting=Count(
                    "team",
                    filter=Q(team__confirmed_at__isnull=False, team__is_waiting=True),
                ),
                competing=Count(
                    "team",
                    filter=Q(team__confirmed_at__isnull=False, team__is_waiting=False),
                ),
                checked_in=Count(
                    "team",
                    filter=Q(team__is_checked_in=True),
                ),
                reviewed=Count(
                    "team",
                    filter=Q(team__is_reviewed=True),
                ),
            )
            .order_by("country", "name", "category__identifier")
        )

        return ctx


class ReleaseNotesView(LoginRequiredMixin, TemplateView):
    template_name = "bullet_admin/home/release_notes.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        with open(settings.BASE_DIR / "CHANGELOG.md") as f:
            ctx["changelog"] = f.read()
        return ctx
