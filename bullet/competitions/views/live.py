from competitions.models import CategoryCompetition, Competition, Venue
from countries.utils import country_reverse
from django.http import HttpResponseBadRequest
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_countries.fields import Country
from problems.models import SolvedProblem
from web import content_blocks


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


class LiveCountdownView(TemplateView):
    template_name = "live/countdown.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = self.competition
        return ctx


class LiveResultsView(TemplateView):
    template_name = "live/results.html"

    def get(self, request, *args, **kwargs):
        self.screens = []
        self.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        venue_codes = request.GET.get("venues", "").upper().split(",")
        venues = {
            v.shortcode: v
            for v in Venue.objects.filter(
                shortcode__in=venue_codes,
                category_competition__competition=self.competition,
            )
            .select_related("category_competition")
            .all()
        }
        categories = []

        content_blocks.load_blocks(request, "category")

        for code in venue_codes:
            if code not in venues:
                return HttpResponseBadRequest(f"Invalid venue {code}.")
            venue: Venue = venues[code]
            if venue.category_competition.identifier not in categories:
                categories.append(venue.category_competition.identifier)

            category_name = content_blocks.get_block(
                request, f"category:name_{venue.category_competition.identifier}"
            )
            url = country_reverse("results_venue", kwargs={"venue": venue.shortcode})
            self.screens.append(
                {
                    "title": f"{venue.name} ({category_name})",
                    "url": f"{url}?embed",
                }
            )

        country = request.GET.get("country")
        if country:
            c = Country(country)
            for category in categories:
                category_name = content_blocks.get_block(
                    request, f"category:name_{category}"
                )
                url = country_reverse(
                    "results_category",
                    kwargs={"category": category, "country": country},
                )
                self.screens.append(
                    {
                        "title": f"{c.name} ({category_name})",
                        "url": f"{url}?embed",
                    }
                )

        international = request.GET.get("international")
        if international in {"1", "true", "yes"}:
            for category in categories:
                category_name = content_blocks.get_block(
                    request, f"category:name_{category}"
                )
                url = country_reverse("results_category", kwargs={"category": category})
                self.screens.append(
                    {
                        "title": f"{_('International')} ({category_name})",
                        "url": f"{url}?embed",
                    }
                )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        ctx["screens"] = [
            self.screens[i : i + 2] for i in range(0, len(self.screens), 2)
        ]
        return ctx


class LiveFirstProblemView(TemplateView):
    template_name = "live/first_problem.html"

    def get(self, request, *args, **kwargs):
        self.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )

        venue_codes = self.request.GET.get("venues", "").upper().split(",")
        venues = {
            v.shortcode: v
            for v in Venue.objects.filter(
                shortcode__in=venue_codes,
                category_competition__competition=self.competition,
            )
            .select_related("category_competition")
            .all()
        }

        self.screens = []
        for code in venue_codes:
            if code not in venues:
                return HttpResponseBadRequest(f"Invalid venue {code}.")

            venue: Venue = venues[code]
            self.screens.append(
                {
                    "category": venue.category_competition.identifier,
                    "problem": SolvedProblem.objects.filter(team__venue=venue)
                    .select_related("team__school")
                    .order_by("competition_time")
                    .first(),
                }
            )

        res = super().get(request, *args, **kwargs)
        return res

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["screens"] = self.screens
        ctx["stop"] = all([s["problem"] is not None for s in self.screens])
        return ctx
