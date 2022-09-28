from bullet_admin.mixins import AnyAdminRequiredMixin
from bullet_admin.utils import get_active_competition
from django.views.generic import ListView
from users.models import Team


class TeamListView(AnyAdminRequiredMixin, ListView):
    template_name = "bullet_admin/teams/list.html"
    paginate_by = 50

    def get_queryset(self):
        competition = get_active_competition(self.request)
        qs = Team.objects.filter(
            competition_venue__category_competition__competition=competition
        )

        crole = self.request.user.get_competition_role(competition)
        if crole.country:
            qs = qs.filter(competition_venue__venue__country=crole.country)
        elif crole.venue:
            qs = qs.filter(competition_venue__venue=crole.venue)

        return qs.select_related(
            "school",
            "competition_venue",
            "competition_venue__category_competition",
            "competition_venue__venue",
        ).prefetch_related("contestants", "contestants__grade")
