from competitions.forms.registration import SchoolSelectForm
from competitions.models import (
    CategoryCompetition,
    CategoryDescription,
    Competition,
    CompetitionVenue,
    Venue,
)
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView
from education.models import School
from users.forms.registration import CategorySelectForm, VenueSelectForm


class RegistrationMixin:
    def setup(self, request, *args, **kwargs):
        self.competition = Competition.objects.get_current_competition(request.BRANCH)

        if self.competition is None:
            raise PermissionDenied()
        if self.competition.registration_start > timezone.now():
            raise PermissionDenied()
        if self.competition.registration_end < timezone.now():
            raise PermissionDenied()

        return super().setup(request, *args, **kwargs)


class HasCategory:
    def setup(self, request, *args, **kwargs):
        if "register_form__category_competition" not in request.session:
            return HttpResponseRedirect(reverse("team_register"))

        self.category_competition = get_object_or_404(
            CategoryCompetition,
            id=request.session["register_form__category_competition"],
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category_competition"] = self.category_competition
        ctx["category_description"] = (
            CategoryDescription.objects.for_request(self.request)
            .filter(category_id=self.category_competition.category_id)
            .first()
        )
        return ctx


class HasVenue:
    def setup(self, request, *args, **kwargs):
        if "register_form__venue" not in request.session:
            return HttpResponseRedirect(reverse("team_register_venue"))

        self.venue = get_object_or_404(
            Venue,
            id=request.session["register_form__venue"],
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["venue"] = self.venue
        return ctx


class CategorySelectView(RegistrationMixin, FormView):
    template_name = "teams/register_category.html"
    form_class = CategorySelectForm

    def dispatch(self, request, *args, **kwargs):
        competition_venues = CompetitionVenue.objects.filter(
            venue__country=request.COUNTRY_CODE.upper(),
            category_competition__competition=self.competition,
        )
        categories = set([c.category_competition_id for c in competition_venues])
        self.categories = (
            CategoryCompetition.objects.filter(id__in=categories)
            .order_by("category__order")
            .select_related("category")
            .all()
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["categories"] = self.categories
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        descriptions = {
            d.category_id: d
            for d in CategoryDescription.objects.for_request(self.request).filter(
                category_id__in=[c.category_id for c in self.categories]
            )
        }
        ctx["categories"] = [
            {
                "category": c,
                "description": descriptions[c.category_id]
                if c.category_id in descriptions
                else None,
            }
            for c in self.categories
        ]
        return ctx

    def form_valid(self, form):
        self.request.session["register_form__category_competition"] = form.cleaned_data[
            "category_competition"
        ]

        return HttpResponseRedirect(reverse("team_register_venue"))


class VenueSelectView(RegistrationMixin, HasCategory, FormView):
    form_class = VenueSelectForm

    def dispatch(self, request, *args, **kwargs):
        self.venues = Venue.objects.filter(
            country=self.request.COUNTRY_CODE.upper(),
            competitionvenue__category_competition=self.category_competition,
        ).order_by("name")

        query = self.request.GET.get("q")
        if query:
            self.venues = self.venues.filter(
                Q(name__icontains=query) | Q(address__raw__icontains=query)
            )

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["venues"] = self.venues
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["venues"] = self.venues
        return ctx

    def form_valid(self, form):
        self.request.session["register_form__venue"] = form.cleaned_data["venue"]
        return HttpResponseRedirect(reverse("team_register_venue"))

    def get_template_names(self):
        if self.request.htmx:
            return ["teams/_register_venues.html"]
        return ["teams/register_venue.html"]

