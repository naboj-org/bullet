from competitions.models import CategoryCompetition, Competition, Venue
from countries.models import BranchCountry
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


class ResultsSelectView(TemplateView):
    template_name = "problems/results/select.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        ctx["categories"] = CategoryCompetition.objects.filter(
            competition=competition, venue__country=self.request.COUNTRY_CODE.upper()
        ).distinct()
        return ctx


class ResultsViewMixin:
    def get_paginate_by(self, queryset):
        if "embed" in self.request.GET:
            return 0
        return 100

    def get_template_names(self):
        if "embed" in self.request.GET:
            return ["problems/results/embed.html"]
        return [self.template_name]


@method_decorator(xframe_options_exempt, name="get")
class CategoryResultsView(ResultsViewMixin, ListView):
    template_name = "problems/results.html"

    def get_competition(self):
        return Competition.objects.get_current_competition(self.request.BRANCH)

    def dispatch(self, request, *args, **kwargs):
        self.country: str = kwargs.get("country")
        if self.country:
            get_object_or_404(
                BranchCountry, branch=request.BRANCH, country=self.country.upper()
            )

        self.competition = self.get_competition()
        self.category = get_object_or_404(
            CategoryCompetition,
            competition=self.competition,
            identifier=self.kwargs["category"],
        )
        self.results_time = results_time(self.competition, timezone.now())

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
        ctx["competition"] = self.competition
        ctx["results_time"] = self.results_time

        ctx["country_name"] = (
            Country(self.country).name if self.country else _("International")
        )
        ctx["country"] = self.country.upper() if self.country else None
        ctx["countries"] = (
            BranchCountry.objects.filter(branch=self.request.BRANCH)
            .order_by("country")
            .all()
        )
        return ctx


@method_decorator(xframe_options_exempt, name="get")
class VenueResultsView(ResultsViewMixin, ListView):
    template_name = "problems/results/venue.html"

    def get_competition(self):
        return Competition.objects.get_current_competition(self.request.BRANCH)

    def dispatch(self, request, *args, **kwargs):
        self.competition = self.get_competition()
        self.venue = get_object_or_404(
            Venue,
            category_competition__competition=self.competition,
            shortcode=self.kwargs["venue"].upper(),
        )
        self.results_time = results_time(
            self.competition, timezone.now(), start_time=self.venue.local_start
        )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_venue_results(self.venue, self.results_time.time)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["team_problem_count"] = self.venue.category_competition.problems_per_team
        ctx["competition"] = self.competition
        ctx["problem_count"] = self.venue.category_competition.problems.count()
        ctx["venue"] = self.venue
        ctx["results_time"] = self.results_time
        return ctx
