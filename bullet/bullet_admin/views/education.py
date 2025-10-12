from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from education.models import School

from bullet import search
from bullet_admin.access import PermissionCheckMixin, is_country_admin
from bullet_admin.forms.education import SchoolForm
from bullet_admin.mixins import MixinProtocol, RedirectBackMixin
from bullet_admin.utils import get_active_competition, get_allowed_countries
from bullet_admin.views import GenericForm
from bullet_admin.views.generic.links import EditIcon, Link, NewLink
from bullet_admin.views.generic.list import GenericList


class SchoolQuerySetMixin(MixinProtocol):
    def get_queryset(self):
        qs = School.objects.filter(is_legacy=False)
        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            qs = qs.filter(country__in=allowed_countries)
        return qs


class SchoolListView(PermissionCheckMixin, SchoolQuerySetMixin, GenericList, ListView):
    required_permissions = [is_country_admin]

    list_links = [NewLink("school", reverse_lazy("badmin:school_create"))]
    table_fields = ["name", "address", "country"]
    table_field_templates = {
        "name": "bullet_admin/education/field__school_name.html",
        "country": "bullet_admin/partials/field__country.html",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by("country", "name", "address")
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.GET.get("q"):
            ctx["page_obj"] = search.nerf_page(ctx["page_obj"])

        return ctx

    def apply_search_filter(self, qs):
        allowed_countries = get_allowed_countries(self.request)

        search_query = self.request.GET.get("q")
        if search_query:
            options = {}
            if allowed_countries is not None:
                country_filter = ",".join([f"'{c}'" for c in allowed_countries])
                options["filter"] = f"country IN [{country_filter}]"
            if order_by := self.request.GET.get("order_by"):
                if order_by.startswith("-"):
                    options["sort"] = [f"{order_by[1:]}:desc"]
                else:
                    options["sort"] = [f"{order_by}:asc"]

            qs = search.MeiliQuerySet(qs, "schools", search_query, options)
        return qs

    def get_row_links(self, obj) -> list[Link]:
        return [EditIcon(reverse("badmin:school_update", args=[obj.pk]))]


class SchoolUpdateView(
    PermissionCheckMixin,
    SchoolQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    UpdateView,
):
    required_permissions = [is_country_admin]
    form_class = SchoolForm
    template_name = "bullet_admin/education/school_form.html"
    form_title = "Edit school"
    require_unlocked_competition = False
    default_success_url = reverse_lazy("badmin:school_list")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        school: School = form.save(commit=False)
        self.object = school
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        messages.success(self.request, "School saved.")
        return HttpResponseRedirect(self.get_success_url())


class SchoolCreateView(
    PermissionCheckMixin,
    SchoolQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    CreateView,
):
    required_permissions = [is_country_admin]
    require_unlocked_competition = False
    form_class = SchoolForm
    form_title = "New school"
    default_success_url = reverse_lazy("badmin:school_list")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        school: School = form.save(commit=False)
        self.object = school
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        messages.success(self.request, "School saved.")
        return HttpResponseRedirect(self.get_success_url())
