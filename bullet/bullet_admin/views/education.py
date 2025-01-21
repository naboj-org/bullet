from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from education.models import School

from bullet import search
from bullet_admin.access import CountryAdminAccess, CountryAdminInAccess
from bullet_admin.forms.education import SchoolForm
from bullet_admin.mixins import RedirectBackMixin
from bullet_admin.utils import get_allowed_countries
from bullet_admin.views import GenericForm, GenericList


class SchoolQuerySetMixin:
    def get_queryset(self):
        return School.objects.filter(is_legacy=False)


class SchoolListView(CountryAdminAccess, SchoolQuerySetMixin, GenericList, ListView):
    require_unlocked_competition = False
    fields = ["name", "address", "country"]
    create_url = reverse_lazy("badmin:school_create")
    field_templates = {
        "name": "bullet_admin/education/school_name.html",
        "country": "bullet_admin/partials/country.html",
    }

    def get_queryset(self):
        qs = super().get_queryset()

        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            qs = qs.filter(country__in=allowed_countries)

        qs = qs.order_by("country", "name", "address")
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.GET.get("q"):
            ctx["page_obj"] = search.nerf_page(ctx["page_obj"])

        return ctx

    def country_navigation(self):
        countries = School.objects.values_list("country", flat=True).distinct()
        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            countries = countries.filter(country__in=allowed_countries)
        return countries

    def get_search_queryset(self, qs):
        allowed_countries = get_allowed_countries(self.request)

        search_query = self.request.GET.get("q")
        if search_query:
            options = {}
            if allowed_countries is not None:
                country_filter = ",".join([f"'{c}'" for c in allowed_countries])
                options["filter"] = f"country IN [{country_filter}]"

            qs = search.MeiliQuerySet(qs, "schools", search_query, options)
        return qs

    def get_edit_url(self, school: School) -> str:
        return reverse("badmin:school_update", args=[school.pk])


class SchoolUpdateView(
    CountryAdminInAccess,
    SchoolQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    UpdateView,
):
    form_class = SchoolForm
    template_name = "bullet_admin/education/school_form.html"
    form_title = "Edit school"
    require_unlocked_competition = False
    default_success_url = reverse_lazy("badmin:school_list")

    def get_permission_country(self):
        return self.get_object().country

    def form_valid(self, form):
        school: School = form.save(commit=False)
        self.object = school
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        messages.success(self.request, "School saved.")
        return HttpResponseRedirect(self.get_success_url())


class SchoolCreateView(
    CountryAdminAccess, SchoolQuerySetMixin, RedirectBackMixin, GenericForm, CreateView
):
    require_unlocked_competition = False
    form_class = SchoolForm
    form_title = "New school"
    default_success_url = reverse_lazy("badmin:school_list")

    def form_valid(self, form):
        school: School = form.save(commit=False)
        self.object = school
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        messages.success(self.request, "School saved.")
        return HttpResponseRedirect(self.get_success_url())
