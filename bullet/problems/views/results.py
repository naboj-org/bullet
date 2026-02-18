from bullet_admin.access import is_operator
from bullet_admin.mixins import MixinProtocol
from bullet_admin.utils import get_active_branch
from competitions.models import Category, Competition, Venue
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView, TemplateView
from django_countries.fields import Country
from users.models.organizers import User

from problems.logic.results import (
    ResultsTime,
    get_category_results,
    get_country_results,
    get_venue_results,
    results_time,
)


class CompetitionMixin(MixinProtocol):
    _competition: Competition

    @property
    def competition(self) -> Competition:
        if not hasattr(self, "_competition"):
            competition = Competition.objects.get_current_competition(
                get_active_branch(self.request)
            )
            if not competition:
                raise ImproperlyConfigured("No active competition.")
            self._competition = competition
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

    def get_results(self):
        raise NotImplementedError()

    def get_category(self):
        raise NotImplementedError()

    def get_venue_timer(self) -> Venue | None:
        return None

    request: HttpRequest

    def get_results_time(self) -> ResultsTime:
        admin = False
        if self.request.GET.get("admin") == "1" and self.request.user.is_authenticated:
            assert isinstance(self.request.user, User)
            admin = is_operator(self.request.user, self.competition)

        start_time = None
        venue = self.get_venue_timer()
        if venue:
            start_time = venue.start_time
        elif venue_code := self.request.GET.get("venue_timer"):
            venue: Venue | None = (
                Venue.objects.for_competition(self.competition)
                .filter(shortcode=venue_code)
                .first()
            )
            if venue:
                start_time = venue.start_time

        return results_time(
            self.competition, timezone.now(), is_admin=admin, start_time=start_time
        )

    def get_queryset(self):
        qs = self.get_results()

        limit = self.request.GET.get("limit", 0)
        try:
            limit = int(limit)
        except ValueError:
            return qs

        if limit <= 0:
            return qs

        return qs[:limit]

    def get_template_names(self):
        if "embed" in self.request.GET:
            return ["problems/results/embed.html"]
        return [self.template_name]

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["start_index"] = ctx["page_obj"].start_index
        ctx["hide_squares"] = self.request.GET.get("hide_squares") == "1"
        ctx["hide_contestants"] = self.request.GET.get("hide_contestants") == "1"

        category = self.get_category()
        ctx["team_problem_count"] = category.problems_per_team
        ctx["first_problem"] = category.first_problem
        ctx["problem_count"] = (
            category.competition.problem_count - category.first_problem + 1
        )
        ctx["results_time"] = self.get_results_time()
        return ctx


@method_decorator(xframe_options_exempt, name="get")
class CategoryResultsView(ResultsViewMixin, ListView):
    template_name = "problems/results.html"

    def get_category(self):
        return self.category

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

        return super().dispatch(request, *args, **kwargs)

    def get_results(self):
        if self.country:
            return get_country_results(
                self.country.upper(), self.category, self.get_results_time().time
            )
        return get_category_results(self.category, self.get_results_time().time)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)

        ctx["category"] = self.category

        ctx["country_name"] = (
            Country(self.country).name if self.country else _("International")
        )
        ctx["country"] = self.country.upper() if self.country else None

        # For non-archive results, competition_number is not in kwargs
        if "competition_number" not in ctx:
            ctx["competition_number"] = None

        return ctx


@method_decorator(xframe_options_exempt, name="get")
class VenueResultsView(ResultsViewMixin, ListView):
    template_name = "problems/results/venue.html"

    def get_category(self):
        return self.venue.category

    def get_venue_timer(self) -> Venue | None:
        return self.venue

    def dispatch(self, request, *args, **kwargs):
        self.venue = get_object_or_404(
            Venue.objects.for_competition(self.competition),
            shortcode=self.kwargs["venue"].upper(),
        )

        return super().dispatch(request, *args, **kwargs)

    def get_results(self):
        return get_venue_results(self.venue, self.get_results_time().time)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["venue"] = self.venue
        # For non-archive results, competition_number is not in kwargs
        if "competition_number" not in ctx:
            ctx["competition_number"] = None
        return ctx
