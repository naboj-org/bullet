from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView, ListView, UpdateView
from education.models import School

from bullet import search
from bullet_admin.access import PermissionCheckMixin, is_country_admin
from bullet_admin.forms.education import SchoolCSVImportForm, SchoolForm
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

    list_links = [
        NewLink("school", reverse_lazy("badmin:school_create")),
        Link("green", "mdi:upload", "Import", reverse_lazy("badmin:school_csv_import")),
    ]
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
        school.save(send_to_search=False)
        form.save_m2m()
        school.send_to_search()

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
        school.save(send_to_search=False)
        form.save_m2m()
        school.send_to_search()

        messages.success(self.request, "School saved.")
        return HttpResponseRedirect(self.get_success_url())


class SchoolCSVImportView(
    PermissionCheckMixin,
    RedirectBackMixin,
    GenericForm,
    FormView,
):
    required_permissions = [is_country_admin]
    form_class = SchoolCSVImportForm
    form_title = "Import schools"
    form_multipart = True
    template_name = "bullet_admin/education/school_csv_import.html"
    default_success_url = reverse_lazy("badmin:school_list")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        if form.cleaned_data["preview"]:
            try:
                schools_data = form.parse_csv()
                return self.render_to_response(
                    self.get_context_data(
                        form=form,
                        preview_data=schools_data[:10],
                    )
                )
            except Exception as e:
                messages.error(self.request, str(e))
                return self.form_invalid(form)
        else:
            try:
                result = form.import_schools()

                if result["errors"]:
                    messages.warning(
                        self.request,
                        f"Import completed with {len(result['errors'])} errors. "
                        f"Created: {result['created']}, Updated: {result['updated']}",
                    )
                    for error in result["errors"][:5]:  # Show first 5 errors
                        messages.error(self.request, error)
                    if len(result["errors"]) > 5:
                        messages.error(
                            self.request,
                            f"... and {len(result['errors']) - 5} more errors",
                        )
                else:
                    messages.success(
                        self.request,
                        f"Successfully imported {result['created']} new schools and updated {result['updated']} existing schools.",
                    )

                return HttpResponseRedirect(self.get_success_url())
            except Exception as e:
                messages.error(self.request, str(e))
                return self.form_invalid(form)
