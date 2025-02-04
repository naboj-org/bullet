from functools import reduce
from operator import attrgetter, or_
from typing import Any, Callable, Protocol

from competitions.models import Competition
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Func, Q
from django.http import HttpRequest, HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django.views.generic.edit import BaseDeleteView
from django_htmx.http import HttpResponseClientRefresh

from bullet_admin.models import CompetitionRole
from bullet_admin.utils import get_active_competition, get_allowed_countries


class MixinProtocol(Protocol):
    request: HttpRequest
    get_context_data: Callable[..., dict]
    get_object: Callable
    get_queryset: Callable
    get_model: Callable


class DeleteView(BaseDeleteView):
    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=["POST"])


class GenericForm(MixinProtocol):
    form_title = None
    form_submit_label = "Save"
    form_submit_icon = "mdi:content-save"
    form_submit_color = "blue"
    form_multipart = False
    template_name = "bullet_admin/generic/form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = self.form_title
        ctx["form_multipart"] = self.form_multipart
        ctx["form_submit_label"] = self.form_submit_label
        ctx["form_submit_icon"] = self.form_submit_icon
        ctx["form_submit_color"] = self.form_submit_color
        return ctx


class GenericDelete(MixinProtocol):
    template_name = "bullet_admin/generic/delete.html"
    model_name = None
    object_name = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_name"] = (
            self.model_name
            if self.model_name
            else self.get_queryset().model._meta.verbose_name
        )
        ctx["object_name"] = (
            self.object_name if self.object_name else str(self.get_object())
        )
        return ctx


class ModelFiltering(MixinProtocol):
    def get_model_fields(self):
        return list(map(attrgetter("name"), self.get_model()._meta.get_fields()))

    def get_filter_q(self, filters: dict[str, Callable[[str], Q]], value: Any) -> Q:
        fields = self.get_model_fields()

        for field, q in filters.items():
            if field in fields:
                return q(value)

        return Q()

    def get_filter_options(
        self, field: str, expansions: dict[str, Func | None]
    ) -> list | None:
        fields = self.get_model_fields()
        qs = self.get_queryset()

        annotated = False
        for field_name, func in expansions.items():
            if field_name in fields:
                if func:
                    qs = qs.annotate(**{field: func})
                annotated = True
                break
        if not annotated:
            return None

        return list(qs.values_list(field, flat=True).order_by(field).distinct())


class CountryNavigation(ModelFiltering, MixinProtocol):
    COUNTRY_FILTERS = {
        "country": lambda c: Q(country=c),
        "countries": lambda c: Q(countries__contains=[c]),
        "team_countries": lambda c: Q(team_countries__contains=[c]),
    }
    COUNTRY_EXPANSIONS = {
        "country": None,
        "countries": Func(F("countries"), function="unnest"),
        "team_countries": Func(F("team_countries"), function="unnest"),
    }

    def apply_country_filter(self, qs):
        country = self.request.GET.get("country")
        if country:
            qs = qs.filter(self.get_filter_q(self.COUNTRY_FILTERS, country))

        # Permission handling
        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            filters = []
            for country in allowed_countries:
                filters.append(self.get_filter_q(self.COUNTRY_FILTERS, country))
            qs = qs.filter(reduce(or_, filters, Q()))

        return qs

    def get_country_navigation(self):
        countries = self.get_filter_options("country", self.COUNTRY_EXPANSIONS)
        if not countries:
            return None

        # Permission handling
        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            countries = list(set(countries) & set(allowed_countries))

        if len(countries) <= 1:
            return None

        countries.sort()
        return countries

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["countries"] = self.get_country_navigation()
        return ctx


class LanguageNavigation(ModelFiltering, MixinProtocol):
    LANGUAGE_FILTER = {
        "language": lambda lang: Q(language=lang),
        "languages": lambda lang: Q(languages__contains=[lang]),
        "team_languages": lambda lang: Q(team_languages__contains=[lang]),
        "accepted_languages": lambda lang: Q(accepted_languages__contains=[lang]),
    }
    LANGUAGE_EXPANSIONS = {
        "language": None,
        "languages": Func(F("languages"), function="unnest"),
        "team_languages": Func(F("team_languages"), function="unnest"),
        "accepted_languages": Func(F("accepted_languages"), function="unnest"),
    }

    def apply_language_filter(self, qs):
        language = self.request.GET.get("language")
        if language:
            qs = qs.filter(self.get_filter_q(self.LANGUAGE_FILTER, language))
        return qs

    def get_language_navigation(self):
        languages = self.get_filter_options("language", self.LANGUAGE_EXPANSIONS)
        if not languages or len(languages) <= 1:
            return None
        return languages

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["languages"] = self.get_language_navigation()
        return ctx


class GenericList(CountryNavigation, LanguageNavigation, MixinProtocol):
    template_name = "bullet_admin/generic/list.html"
    paginate_by = 100
    list_title = None
    object_name = None
    help_url = None
    create_url = None
    upload_url = None
    export_url = None
    new_folder_url = None
    assign_numbers_url = None
    subtitle = None
    labels = {}
    fields = []
    edit_urls = []
    delete_urls = []
    view_urls = []
    field_templates = {}
    view_type = "view"

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = {}
        qs = self.get_queryset()
        if object_list:
            qs = object_list
        qs = self.apply_country_filter(qs)
        qs = self.apply_language_filter(qs)
        qs = self.get_orderby_queryset(qs)
        ctx["count"] = qs.count()
        qs = self.get_search_queryset(qs)

        ctx |= super().get_context_data(object_list=qs, **kwargs)

        ctx["orderby"] = self.request.GET.get("orderby")
        ctx["table_row"] = map(self.create_row, ctx["object_list"])
        ctx["list_title"] = self.get_list_title()
        ctx["object_name"] = self.get_object_name()
        ctx["help_url"] = self.help_url
        ctx["create_url"] = self.create_url
        ctx["upload_url"] = self.upload_url
        ctx["export_url"] = self.export_url
        ctx["new_folder_url"] = self.new_folder_url
        ctx["assign_numbers_url"] = self.assign_numbers_url
        ctx["subtitle"] = self.subtitle
        ctx["labels"] = self.get_labels()
        ctx["view_type"] = self.view_type

        return ctx

    def get_orderby_queryset(self, qs):
        orderby = self.request.GET.get("orderby")
        if orderby:
            return qs.order_by(orderby)
        return qs

    def get_search_queryset(self, qs):
        search = self.request.GET.get("q")
        if search:
            big_query = Q()
            for word in search.split():
                query = Q()
                for field in self.get_model()._meta.get_fields():
                    if type(field).__name__ not in [
                        "ManyToOneRel",
                        "ForeignKey",
                        "ManyToManyField",
                        "ManyToManyRel",
                        "OneToOneRel",
                    ]:
                        field__icontains = field.name + "__icontains"
                        query |= Q(**{field__icontains: word})
                big_query &= query
            qs = qs.filter(big_query)
        return qs

    @cached_property
    def get_model(self):
        return self.model if self.model else self.get_queryset().model

    def get_list_title(self):
        return (
            self.list_title
            if self.list_title
            else self.get_model()._meta.verbose_name_plural.capitalize()
        )

    def get_fields(self):
        return (
            self.fields
            if self.fields
            else [field.name for field in self.get_model()._meta.get_fields()]
        )

    def get_object_name(self):
        return (
            self.object_name
            if self.object_name
            else self.get_list_title().split(" ")[-1].lower()[0:-1]
        )

    def get_labels(self):
        return [
            (
                self.labels[field]
                if field in self.labels
                else field.replace("_", " ").capitalize(),
                field,
            )
            for field in self.get_fields()
        ]

    def create_row(self, object):
        return [
            [
                getattr(object, field)
                if field not in self.field_templates
                else mark_safe(
                    render_to_string(self.field_templates[field], {"object": object})
                )
                for field in self.get_fields()
            ],
            self.get_edit_url(object),
            self.get_delete_url(object),
            self.get_view_url(object),
            self.get_download_url(object),
            self.get_generate_url(object),
        ]

    def get_edit_url(self, obj) -> str | None:
        return None

    def get_delete_url(self, obj) -> str | None:
        return None

    def get_view_url(self, obj) -> str | None:
        return None

    def get_download_url(self, obj) -> str | None:
        return None

    def get_generate_url(self, obj) -> str | None:
        return None


class CompetitionSwitchView(LoginRequiredMixin, TemplateView):
    template_name = "bullet_admin/competition_switch.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.user.get_branch_role(self.request.BRANCH).is_admin:
            ctx["competitions"] = Competition.objects.filter(
                branch=self.request.BRANCH
            ).order_by("-competition_start")
            ctx["branch_admin"] = True
        else:
            ctx["branch_admin"] = False

        ctx["roles"] = (
            CompetitionRole.objects.filter(
                user=self.request.user, competition__branch=self.request.BRANCH
            )
            .select_related("competition")
            .prefetch_related("venue_objects")
            .order_by("-competition__competition_start")
            .all()
        )
        ctx["active"] = get_active_competition(self.request)
        return ctx

    def post(self, request, *args, **kwargs):
        if "competition" in request.GET:
            request.session[
                f"badmin_{request.BRANCH.identifier}_competition"
            ] = request.GET.get("competition")
        return HttpResponseClientRefresh()
