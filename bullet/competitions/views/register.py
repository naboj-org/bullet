from enum import IntEnum
from functools import partial

from bullet_admin.access_v2 import is_admin
from countries.utils import country_reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView
from education.models import School
from users.emails.teams import send_confirmation_email

from bullet import search
from competitions.forms.registration import (
    CategorySelectForm,
    ContestantForm,
    SchoolSelectForm,
    VenueSelectForm,
)
from competitions.models import Category, Competition, Venue


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

        # Admin can register at any time
        if request.user.is_authenticated and is_admin(request.user, competition):
            return competition

        if competition.registration_start > timezone.now():
            raise RegistrationError(_("Registration did not start yet."))
        if competition.registration_end < timezone.now():
            raise RegistrationError(_("Registration is over."))
        return competition

    def _load_category(self, request) -> Category:
        if "category" not in request.session["register_form"]:
            raise RegistrationError()

        cc = Category.objects.filter(
            id=request.session["register_form"]["category"],
            competition=self.competition,
        ).first()

        if not cc:
            raise RegistrationError()

        return cc

    def _load_venue(self, request) -> Venue:
        if "venue" not in request.session["register_form"]:
            raise RegistrationError()

        venue = (
            Venue.objects.for_competition(self.competition)
            .filter(
                id=request.session["register_form"]["venue"],
                country=request.COUNTRY_CODE.upper(),
                category=self.category,
            )
            .first()
        )

        if not venue:
            raise RegistrationError()

        return venue

    def _load_school(self, request) -> School:
        if "school" not in request.session["register_form"]:
            raise RegistrationError()

        school = School.objects.filter(
            id=request.session["register_form"]["school"],
            is_hidden=False,
            country=request.COUNTRY_CODE.upper(),
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
            self.competition = self._load_competition(request)
        except RegistrationError as e:
            messages.add_message(request, messages.ERROR, e.messsage)
            return country_reverse("homepage")

        try:
            if self.registration_step >= RegistrationStep.CATEGORY:
                self.category = self._load_category(request)
            if self.registration_step >= RegistrationStep.VENUE:
                self.venue = self._load_venue(request)
            if self.registration_step >= RegistrationStep.SCHOOL:
                self.school = self._load_school(request)
        except RegistrationError:
            # We ignore error message here to avoid user confusion.
            return country_reverse("register")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["competition"] = self.competition

        if self.registration_step >= RegistrationStep.CATEGORY:
            ctx["category"] = self.category

        if self.registration_step >= RegistrationStep.VENUE:
            ctx["venue"] = self.venue

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

        venues = Venue.objects.for_competition(self.competition).filter(
            country=self.request.COUNTRY_CODE.upper()
        )
        categories = set([c.category_id for c in venues])
        self.categories = (
            Category.objects.filter(id__in=categories).order_by("order").all()
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
        self.request.session["register_form"]["category"] = form.cleaned_data[
            "category"
        ]
        self.request.session.modified = True

        return HttpResponseRedirect(country_reverse("register_venue"))


class VenueSelectView(RegistrationMixin, FormView):
    form_class = VenueSelectForm
    registration_step = RegistrationStep.CATEGORY

    def dispatch(self, request, *args, **kwargs):
        red = self.prepare_models(request)
        if red:
            return HttpResponseRedirect(red)

        self.venues = Venue.objects.for_competition(self.competition).filter(
            country=self.request.COUNTRY_CODE.upper(),
            category=self.category,
        )

        query = self.request.GET.get("q")
        if query:
            self.venues = self.venues.filter(
                Q(name__icontains=query) | Q(address__icontains=query)
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
        return HttpResponseRedirect(country_reverse("register_school"))

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
        ctx["schools"] = []
        query = self.request.GET.get("q")

        allowed_types = set(
            self.category.educations.values_list(
                "grades__school_type_id", flat=True
            ).distinct()
        )
        allowed_types = ",".join(map(str, allowed_types))

        if query:
            result = search.client.index("schools").search(
                query,
                {
                    "filter": [
                        f"country = '{self.request.COUNTRY_CODE.upper()}'",
                        "is_hidden = false",
                        f"types IN [{allowed_types}]",
                    ]
                },
            )
            ctx["schools"] = result["hits"]

        return ctx

    def form_valid(self, form):
        self.request.session["register_form"]["school"] = form.cleaned_data["school"]
        self.request.session.modified = True
        return HttpResponseRedirect(country_reverse("register_details"))

    def get_template_names(self):
        if self.request.htmx:
            return ["register/_school.html"]
        return ["register/school.html"]


class TeamDetailsView(RegistrationMixin, FormView):
    template_name = "register/details.html"
    registration_step = RegistrationStep.SCHOOL

    def get_form_class(self):
        flow = self.venue.registration_flow
        return flow.get_form()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = self.get_formset()
        return ctx

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["venue"] = self.venue
        return kw

    def get_formset(self):
        return formset_factory(
            ContestantForm,
            min_num=0,
            max_num=self.category.max_members_per_team,
            extra=self.category.max_members_per_team,
            validate_max=True,
        )(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {
            "form_kwargs": {
                "school_types": self.school.types.prefetch_related("grades"),
                "category": self.category,
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
        team.venue = self.venue
        team.consent_photos = "consent_photos" in self.request.POST
        team.save()

        if hasattr(form, "save_related"):
            form.save_related()

        for contestant_form in formset:
            if not contestant_form.has_changed():
                continue

            contestant = contestant_form.save(commit=False)
            contestant.team = team
            contestant.save()

        transaction.on_commit(partial(send_confirmation_email.delay, team.id))
        del self.request.session["register_form"]
        return HttpResponseRedirect(country_reverse("register_thanks"))


class ThanksView(RegistrationMixin, TemplateView):
    template_name = "register/thanks.html"
