from bullet_admin.access import AdminAccess, VenueAccess
from bullet_admin.utils import get_active_competition
from competitions.models import Category, Venue
from countries.models import BranchCountry
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from problems.logic.results import get_venue_results


class ResultsHomeView(AdminAccess, TemplateView):
    template_name = "bullet_admin/results/select.html"
    allow_operator = True
    require_unlocked_competition = False

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


class ResultsAnnouncementView(VenueAccess, TemplateView):
    template_name = "bullet_admin/results/announce.html"
    allow_operator = True
    require_unlocked_competition = False

    @cached_property
    def venue(self):
        return get_object_or_404(Venue, id=self.kwargs["venue"])

    def get_permission_venue(self) -> "Venue":
        return self.venue

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
