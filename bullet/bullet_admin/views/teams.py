from bullet_admin.mixins import AnyAdminRequiredMixin
from bullet_admin.utils import get_active_competition
from django.views.generic import ListView
from users.models import Team


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

        return qs.select_related(
            "school",
            "venue",
            "venue__category_competition",
        ).prefetch_related("contestants", "contestants__grade")

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["hide_venue"] = (
            self.request.user.get_competition_role(
                get_active_competition(self.request)
            ).venue
            is not None
        )
        return ctx
