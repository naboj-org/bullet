from competitions.models import Category, Competition
from django.core.files.storage import default_storage
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django.views.generic import ListView

from problems.models import ProblemStat, ProblemStatement
from problems.views.results import (
    CategoryResultsView,
    ResultsSelectView,
    VenueResultsView,
)


class ArchiveCompetitionMixin:
    @property
    def competition(self):
        if not hasattr(self, "_competition"):
            self._competition = get_object_or_404(
                Competition.objects.for_user(self.request.user, self.request.BRANCH),
                number=self.kwargs["competition_number"],
            )
        return self._competition

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition_number"] = self.competition.number
        ctx["competition"] = self.competition
        return ctx


class ArchiveResultsSelectView(ArchiveCompetitionMixin, ResultsSelectView):
    pass


class ArchiveCategoryResultsView(ArchiveCompetitionMixin, CategoryResultsView):
    pass


class ArchiveVenueResultsView(ArchiveCompetitionMixin, VenueResultsView):
    pass


class ProblemStatementView(ArchiveCompetitionMixin, ListView):
    template_name = "archive/problems.html"

    def get_queryset(self):
        return ProblemStatement.objects.filter(
            problem__competition=self.competition, language=get_language()
        ).prefetch_related(
            "problem__category_problems", "problem__category_problems__category"
        )

    def inject_stats(self, object_list):
        stats = (
            ProblemStat.objects.filter(problem__in=object_list.values("problem"))
            .values("problem")
            .annotate(
                received=Count("*"),
                solved=Count("solved_time"),
                avg_time=Avg("solve_duration"),
            )
        )
        stats = {s["problem"]: s for s in stats}

        new_list = []
        for obj in object_list:
            obj.stats = stats.get(obj.problem.id)
            new_list.append(obj)

        return new_list

    def order_problems(self, problem_list: list[ProblemStatement]):
        reference_category = (
            Category.objects.filter(competition=self.competition)
            .annotate(problem_count=Count("problems"))
            .order_by("-problem_count")
            .first()
        )
        problems = reference_category.problems.all()
        problem_order = {p.problem_id: p.number for p in problems}
        problem_list.sort(key=lambda p: problem_order.get(p.problem_id, 99999))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_list"] = self.inject_stats(ctx["object_list"])
        self.order_problems(ctx["object_list"])

        pdf_file = self.competition.secret_dir / f"problems-{get_language()}.pdf"
        if default_storage.exists(pdf_file):
            ctx["pdf"] = default_storage.url(pdf_file)
        return ctx
