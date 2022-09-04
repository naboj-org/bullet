from competitions.models import CategoryCompetition, Competition, CompetitionVenue
from django.views.generic import TemplateView


class TeamList(TemplateView):
    template_name = "web/team_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        competition: Competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        ctx["sites"] = (
            CompetitionVenue.objects.filter(
                category_competition__competition=competition
            )
            .order_by("site__name")
            .all()
        )
        total_teams = 0
        for site in ctx["sites"]:
            total_teams += site.team_set.count()
        ctx["total_teams"] = total_teams
        ctx["countries"] = set(
            [site.site.address.locality.state.country for site in ctx["sites"]]
        )
        ctx["categories"] = CategoryCompetition.objects.filter(
            competition=competition
        ).all()
        return ctx
