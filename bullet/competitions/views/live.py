from competitions.models import CategoryCompetition, Competition
from countries.utils import country_reverse
from django.views.generic import TemplateView


class LiveView(TemplateView):
    template_name = "live.html"

    def dispatch(self, request, *args, **kwargs):
        self.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        return super().dispatch(request, *args, **kwargs)

    def get_screens(self):
        screens = []
        categories = (
            CategoryCompetition.objects.filter(competition=self.competition)
            .order_by("order")
            .values_list("identifier", flat=True)
        )

        if self.request.GET.get("international", "0") == "1":
            screens.extend(
                [
                    country_reverse("results_category", kwargs={"category": c})
                    for c in categories
                ]
            )

        if "countries" in self.request.GET:
            for country in self.request.GET["countries"].split(","):
                screens.extend(
                    [
                        country_reverse(
                            "results_category",
                            kwargs={"category": c, "country": country.lower()},
                        )
                        for c in categories
                    ]
                )

        if "venues" in self.request.GET:
            screens.extend(
                [
                    country_reverse("results_venue", kwargs={"venue": v.lower()})
                    for v in self.request.GET["venues"].split(",")
                ]
            )
        return screens

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = self.competition
        ctx["screens"] = self.get_screens()
        return ctx
