from bullet_admin.forms.utils import get_venue_queryset
from competitions.models import Competition
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "bullet_admin/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        ctx["competition"] = competition
        ctx["venues"] = get_venue_queryset(competition, self.request.user).annotate(
            registered=Count("team"),
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
