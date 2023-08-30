from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from competitions.models import Category, Venue
from countries.models import BranchCountry
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from problems.logic.results import get_venue_results


class ResultsHomeView(AdminRequiredMixin, TemplateView):
    template_name = "bullet_admin/results/select.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        competition = get_active_competition(self.request)

        country = BranchCountry.objects.filter(branch=self.request.BRANCH).first()
        ctx["country"] = country.country.code.lower()
        ctx["language"] = country.languages[0]

        ctx["venues"] = Venue.objects.for_competition(competition)
        ctx["my_venues"] = Venue.objects.for_request(self.request)
        ctx["categories"] = Category.objects.filter(competition=competition)
        return ctx


class ResultsAnnouncementView(AdminRequiredMixin, TemplateView):
    template_name = "bullet_admin/results/announce.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.can_access():
            return self.handle_fail()

        self.venue = get_object_or_404(Venue, id=kwargs["venue"])
        if not can_access_venue(request, self.venue):
            return self.handle_fail()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["venue"] = self.venue
        position = self.request.GET.get("position", "1")
        hidden = "hidden" in self.request.GET
        try:
            position = int(position)
        except ValueError:
            raise Http404()

        ctx["hidden"] = hidden
        ctx["position"] = position
        try:
            ctx["team"] = get_venue_results(self.venue)[position - 1].team
        except IndexError:
            ctx["team"] = None

        r = reverse("badmin:results_announce", kwargs={"venue": self.venue.id})
        ctx["links"] = {
            "prev": f"{r}?position={position + 1}{'&hidden' if hidden else ''}",
            "hide": f"{r}?position={position}{'&hidden' if not hidden else ''}",
            "next": f"{r}?position={max(1, position - 1)}{'&hidden' if hidden else ''}",
        }
        return ctx
