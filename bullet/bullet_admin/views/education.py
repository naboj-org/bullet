from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, UpdateView
from education.models import School

from bullet import search
from bullet_admin.access import CountryAdminAccess, CountryAdminInAccess
from bullet_admin.forms.education import SchoolForm
from bullet_admin.utils import get_allowed_countries
from bullet_admin.views import GenericForm


class SchoolQuerySetMixin:
    def get_queryset(self):
        return School.objects.filter(is_legacy=False)


class SchoolListView(CountryAdminAccess, SchoolQuerySetMixin, ListView):
    template_name = "bullet_admin/education/school_list.html"
    paginate_by = 100
    require_unlocked_competition = False

    def get_queryset(self):
        qs = super().get_queryset()

        country = self.request.GET.get("country")
        if country:
            qs = qs.filter(country=country)

        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            qs = qs.filter(country__in=allowed_countries)

        search_query = self.request.GET.get("q")
        if search_query:
            options = {}
            if allowed_countries is not None:
                country_filter = ",".join([f"'{c}'" for c in allowed_countries])
                options["filter"] = f"country IN [{country_filter}]"

            qs = search.MeiliQuerySet(qs, "schools", search_query, options)
        else:
            qs = qs.order_by("country", "name", "address")
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["school_count"] = School.objects.count()

        countries = School.objects.values_list("country", flat=True).distinct()
        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            countries = countries.filter(country__in=allowed_countries)
        ctx["countries"] = countries

        if self.request.GET.get("q"):
            ctx["page_obj"] = search.nerf_page(ctx["page_obj"])

        return ctx


class SchoolUpdateView(
    CountryAdminInAccess, SchoolQuerySetMixin, GenericForm, UpdateView
):
    form_class = SchoolForm
    template_name = "bullet_admin/education/school_form.html"
    form_title = "Edit school"
    require_unlocked_competition = False

    def get_permission_country(self):
        return self.get_object().country

    def form_valid(self, form):
        school: School = form.save(commit=False)
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        return redirect("badmin:school_list")


class SchoolCreateView(
    CountryAdminAccess, SchoolQuerySetMixin, GenericForm, CreateView
):
    require_unlocked_competition = False
    form_class = SchoolForm
    form_title = "New school"

    def form_valid(self, form):
        school: School = form.save(commit=False)
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        return redirect("badmin:school_list")
