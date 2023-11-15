from competitions.models import Competition, Venue
from countries.utils import country_reverse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView
from django_countries.fields import Country
from problems.models import SolvedProblem
from web import content_blocks


class LiveView(TemplateView):
    template_name = "live.html"

    def get(self, request, *args, **kwargs):
        self.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )

        venue_timer = request.GET.get("venue_timer", "").upper()
        self.start_time = self.competition.competition_start

        if venue_timer:
            venue = (
                Venue.objects.for_competition(self.competition)
                .filter(shortcode=venue_timer)
                .first()
            )
            self.start_time = venue.start_time

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = self.competition
        query = ctx["query"] = f"?{self.request.GET.urlencode()}"
        ctx["data"] = {
            "countdown": country_reverse("live_countdown") + query,
            "results": country_reverse("live_results") + query,
            "first_problem": country_reverse("live_first_problem") + query,
            "start": self.start_time,
            "duration": self.competition.competition_duration.total_seconds(),
        }
        return ctx


@method_decorator(xframe_options_exempt, name="get")
class LiveCountdownView(TemplateView):
    template_name = "live/countdown.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        return ctx


@method_decorator(xframe_options_exempt, name="get")
class LiveResultsView(TemplateView):
    template_name = "live/results.html"

    def get(self, request, *args, **kwargs):
        self.screens = []
        self.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        venue_codes = request.GET.get("venues", "")
        if venue_codes:
            venue_codes = venue_codes.upper().split(",")
        else:
            venue_codes = []
        venues = {
            v.shortcode: v
            for v in Venue.objects.for_competition(self.competition).filter(
                shortcode__in=venue_codes
            )
        }
        categories = []
        content_blocks.load_blocks(request, "category")

        query = {"embed": 1}
        venue_timer = request.GET.get("venue_timer")
        if venue_timer:
            query["venue_timer"] = venue_timer
        query = urlencode(query)

        for code in venue_codes:
            if code not in venues:
                return HttpResponseBadRequest(f"Invalid venue {code}.")
            venue: Venue = venues[code]
            if venue.category.identifier not in categories:
                categories.append(venue.category.identifier)

            category_name = content_blocks.get_block(
                request, f"category:name_{venue.category.identifier}"
            )
            url = country_reverse("results_venue", kwargs={"venue": venue.shortcode})
            self.screens.append(
                {
                    "title": f"{venue.name} ({category_name})",
                    "url": f"{url}?{query}",
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
                        "url": f"{url}?{query}",
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
                        "url": f"{url}?{query}",
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


@method_decorator(xframe_options_exempt, name="get")
class LiveFirstProblemView(TemplateView):
    template_name = "live/first_problem.html"

    def get(self, request, *args, **kwargs):
        self.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )

        venue_codes = self.request.GET.get("venues", "").upper().split(",")
        venues = {
            v.shortcode: v
            for v in Venue.objects.for_competition(self.competition)
            .filter(shortcode__in=venue_codes)
            .select_related("category")
            .all()
        }

        self.screens = []
        for code in venue_codes:
            if code not in venues:
                return HttpResponseBadRequest(f"Invalid venue {code}.")

            venue: Venue = venues[code]
            self.screens.append(
                {
                    "category": venue.category.identifier,
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
