from bullet_admin.access import is_any_admin
from competitions.models import Category, Competition, Venue
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView, TemplateView
from django_countries.fields import Country

from problems.logic.results import (
    get_category_results,
    get_country_results,
    get_venue_results,
    results_time,
)


class CompetitionMixin:
    @property
    def competition(self) -> Competition:
        if not hasattr(self, "_competition"):
            self._competition = Competition.objects.get_current_competition(
                self.request.BRANCH
            )
        return self._competition

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = self.competition
        return ctx


class ResultsSelectView(CompetitionMixin, TemplateView):
    template_name = "problems/results/select.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        competition = self.competition
        ctx["categories"] = Category.objects.filter(
            competition=competition, venue__country=self.request.COUNTRY_CODE.upper()
        ).distinct()
        return ctx


class ResultsViewMixin(CompetitionMixin):
    paginate_by = 100

    def get_template_names(self):
        if "embed" in self.request.GET:
            return ["problems/results/embed.html"]
        return [self.template_name]

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["start_index"] = ctx["page_obj"].start_index
        return ctx


@method_decorator(xframe_options_exempt, name="get")
class CategoryResultsView(ResultsViewMixin, ListView):
    template_name = "problems/results.html"

    def dispatch(self, request, *args, **kwargs):
        self.country: str = kwargs.get("country")
        if self.country:
            if not Venue.objects.filter(
                category__competition=self.competition, country=self.country.upper()
            ).exists():
                raise Http404()

        self.category = get_object_or_404(
            Category,
            competition=self.competition,
            identifier=self.kwargs["category"],
        )

        admin = False
        if request.GET.get("admin") == "1":
            admin = is_any_admin(
                self.request.user, self.competition, allow_operator=True
            )

        start_time = None
        if "venue_timer" in request.GET:
            start_time = (
                Venue.objects.for_competition(self.competition)
                .filter(shortcode=request.GET["venue_timer"])
                .first()
            )
            if start_time:
                start_time = start_time.start_time

        self.results_time = results_time(
            self.competition, timezone.now(), is_admin=admin, start_time=start_time
        )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.country:
            return get_country_results(
                self.country.upper(), self.category, self.results_time.time
            )
        return get_category_results(self.category, self.results_time.time)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["team_problem_count"] = self.category.problems_per_team
        ctx["problem_count"] = self.category.problems.count()
        ctx["category"] = self.category
        ctx["results_time"] = self.results_time

        ctx["country_name"] = (
            Country(self.country).name if self.country else _("International")
        )
        ctx["country"] = self.country.upper() if self.country else None
        ctx["countries"] = [
            Country(c)
            for c in Venue.objects.filter(category__competition=self.competition)
            .order_by("country")
            .distinct("country")
            .values_list("country", flat=True)
        ]
        return ctx


@method_decorator(xframe_options_exempt, name="get")
class VenueResultsView(ResultsViewMixin, ListView):
    template_name = "problems/results/venue.html"

    def dispatch(self, request, *args, **kwargs):
        self.venue = get_object_or_404(
            Venue.objects.for_competition(self.competition),
            shortcode=self.kwargs["venue"].upper(),
        )

        admin = False
        if request.GET.get("admin") == "1":
            admin = is_any_admin(
                self.request.user, self.competition, allow_operator=True
            )
        self.results_time = results_time(
            self.competition,
            timezone.now(),
            start_time=self.venue.local_start,
            is_admin=admin,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_venue_results(self.venue, self.results_time.time)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["team_problem_count"] = self.venue.category.problems_per_team
        ctx["problem_count"] = self.venue.category.problems.count()
        ctx["venue"] = self.venue
        ctx["results_time"] = self.results_time
        return ctx
