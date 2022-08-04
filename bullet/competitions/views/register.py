from enum import IntEnum

from competitions.forms.registration import (
    CategorySelectForm,
    ParticipantForm,
    RegistrationForm,
    SchoolSelectForm,
    VenueSelectForm,
)
from competitions.models import (
    CategoryCompetition,
    CategoryDescription,
    Competition,
    CompetitionVenue,
    Venue,
)
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView
from education.models import School


class RegistrationError(Exception):
    def __init__(self, message=None):
        self.messsage = message


class RegistrationStep(IntEnum):
    NONE = 0
    CATEGORY = 1
    VENUE = 2
    SCHOOL = 3


class RegistrationMixin:
    registration_step = RegistrationStep.NONE

    def _load_competition(self, request) -> Competition:
        competition = Competition.objects.get_current_competition(request.BRANCH)

        if competition is None:
            # Not translated as this should not happen in production.
            raise RegistrationError("No competitions in database.")
        if competition.registration_start > timezone.now():
            raise RegistrationError(_("Registration did not start yet."))
        if competition.registration_end < timezone.now():
            raise RegistrationError(_("Registration is over."))

        return competition

    def _load_category(self, request) -> CategoryCompetition:
        if "category_competition" not in request.session["register_form"]:
            raise RegistrationError()

        cc = CategoryCompetition.objects.filter(
            id=request.session["register_form"]["category_competition"]
        ).first()

        if not cc:
            raise RegistrationError()

        return cc

    def _load_venue(self, request) -> tuple[CompetitionVenue, Venue]:
        if "venue" not in request.session["register_form"]:
            raise RegistrationError()

        competition_venue = CompetitionVenue.objects.filter(
            id=request.session["register_form"]["venue"],
        ).first()

        if not competition_venue:
            raise RegistrationError()
        if competition_venue.category_competition.competition_id != self.competition.id:
            raise RegistrationError()

        return competition_venue, competition_venue.venue

    def _load_school(self, request) -> School:
        if "school" not in request.session["register_form"]:
            raise RegistrationError()

        school = School.objects.filter(
            id=request.session["register_form"]["school"],
        ).first()

        if school is None:
            raise RegistrationError()

        return school

    def prepare_models(self, request) -> str | None:
        """
        Loads all required model objects.

        Returns target URL if redirect is needed, None otherwise.
        """
        if hasattr(self, "competition"):
            return None

        if "register_form" not in request.session:
            request.session["register_form"] = {}

        try:
            self.competition = self._load_competition()
        except RegistrationError as e:
            messages.add_message(request, messages.ERROR, e.messsage)
            return reverse("homepage")

        try:
            if self.registration_step >= RegistrationStep.CATEGORY:
                self.category_competition = self._load_category(request)
            if self.registration_step >= RegistrationStep.VENUE:
                self.competition_venue, self.venue = self._load_venue(request)
            if self.registration_step >= RegistrationStep.SCHOOL:
                self.school = self._load_school(request)
        except RegistrationError:
            # We ignore error message here to avoid user confusion.
            return reverse("register")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = self.competition

        if self.registration_step >= RegistrationStep.CATEGORY:
            ctx["category_competition"] = self.category_competition
            ctx["category_description"] = (
                CategoryDescription.objects.for_request(self.request)
                .filter(category_id=self.category_competition.category_id)
                .first()
            )

        if self.registration_step >= RegistrationStep.VENUE:
            ctx["venue"] = self.venue
            ctx["competition_venue"] = self.competition_venue

        if self.registration_step >= RegistrationStep.SCHOOL:
            ctx["school"] = self.school

        return ctx

    def dispatch(self, request, *args, **kwargs):
        red = self.prepare_models(request)
        if red:
            return HttpResponseRedirect(red)
        return super().dispatch(request, *args, **kwargs)


class CategorySelectView(RegistrationMixin, FormView):
    template_name = "register/category.html"
    form_class = CategorySelectForm

    def dispatch(self, request, *args, **kwargs):
        red = self.prepare_models(request)
        if red:
            return HttpResponseRedirect(red)

        competition_venues = CompetitionVenue.objects.filter(
            venue__country=self.request.COUNTRY_CODE.upper(),
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
        ctx["categories"] = self.categories
        return ctx

    def form_valid(self, form):
        self.request.session["register_form"][
            "category_competition"
        ] = form.cleaned_data["category_competition"]
        self.request.session.modified = True

        return HttpResponseRedirect(reverse("register_venue"))


class VenueSelectView(RegistrationMixin, FormView):
    form_class = VenueSelectForm
    registration_step = RegistrationStep.CATEGORY

    def dispatch(self, request, *args, **kwargs):
        red = self.prepare_models(request)
        if red:
            return HttpResponseRedirect(red)

        self.venues = CompetitionVenue.objects.filter(
            category_competition=self.category_competition,
            venue__country=self.request.COUNTRY_CODE.upper(),
        ).order_by("venue__name")

        query = self.request.GET.get("q")
        if query:
            self.venues = self.venues.filter(
                Q(venue__name__icontains=query)
                | Q(venue__address__raw__icontains=query)
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
        self.request.session["register_form"]["venue"] = form.cleaned_data["venue"]
        self.request.session.modified = True
        return HttpResponseRedirect(reverse("register_school"))

    def get_template_names(self):
        if self.request.htmx:
            return ["register/_venue.html"]
        return ["register/venue.html"]


class SchoolSelectView(RegistrationMixin, FormView):
    form_class = SchoolSelectForm
    registration_step = RegistrationStep.VENUE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["country"] = self.request.COUNTRY_CODE.upper()
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        schools = []
        query = self.request.GET.get("q")

        if query:
            schools = School.objects.filter(
                country=self.request.COUNTRY_CODE.upper()
            ).filter(Q(name__icontains=query) | Q(address__raw__icontains=query))[:25]

        ctx["schools"] = schools
        return ctx

    def form_valid(self, form):
        self.request.session["register_form"]["school"] = form.cleaned_data["school"]
        self.request.session.modified = True
        return HttpResponseRedirect(reverse("register_details"))

    def get_template_names(self):
        if self.request.htmx:
            return ["register/_school.html"]
        return ["register/school.html"]


class TeamDetailsView(RegistrationMixin, FormView):
    template_name = "register/details.html"
    form_class = RegistrationForm
    registration_step = RegistrationStep.SCHOOL

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = self.get_formset()
        return ctx

    def get_formset(self):
        return formset_factory(
            ParticipantForm,
            min_num=0,
            max_num=self.category_competition.max_members_per_team,
            extra=self.category_competition.max_members_per_team,
            validate_max=True,
        )(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {
            "form_kwargs": {
                "school_types": self.school.types.prefetch_related("grades"),
            }
        }
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.forms_valid(form, formset)
        else:
            return self.form_invalid(form)

    @transaction.atomic
    def forms_valid(self, form, formset):
        team = form.save(commit=False)
        team.school = self.school
        team.competition_venue = self.competition_venue
        team.save()

        for participant_form in formset:
            if not participant_form.has_changed():
                continue

            participant = participant_form.save(commit=False)
            participant.team = team
            participant.save()

        del self.request.session["register_form"]
        return HttpResponseRedirect(reverse("register_thanks"))


class ThanksView(RegistrationMixin, TemplateView):
    template_name = "register/thanks.html"
