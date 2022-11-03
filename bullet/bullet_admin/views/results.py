from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import get_active_competition
from competitions.models import CategoryCompetition, Venue
from countries.models import BranchCountry
from django.views.generic import TemplateView


class ResultsHomeView(AdminRequiredMixin, TemplateView):
    template_name = "bullet_admin/results/select.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        competition = get_active_competition(self.request)

        country = BranchCountry.objects.filter(branch=self.request.BRANCH).first()
        ctx["country"] = country.country.code.lower()
        ctx["language"] = country.languages[0]

        ctx["venues"] = (
            Venue.objects.filter(category_competition__competition=competition)
            .order_by("name", "category_competition__identifier")
            .select_related("category_competition")
        )
        ctx["categories"] = CategoryCompetition.objects.filter(competition=competition)
        return ctx
