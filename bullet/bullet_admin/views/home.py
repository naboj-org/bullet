from bullet_admin.utils import get_active_competition
from competitions.models import Venue
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "bullet_admin/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["competition"] = get_active_competition(self.request)
        ctx["venues"] = Venue.objects.for_request(self.request).annotate(
            registered=Count("team", filter=Q(team__confirmed_at__isnull=False)),
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

        return ctx
