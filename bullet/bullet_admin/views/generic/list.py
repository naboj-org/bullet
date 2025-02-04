import warnings
from functools import reduce
from operator import attrgetter, or_
from typing import Any, Callable

from django.db.models import F, Func, Q
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from bullet_admin.mixins import MixinProtocol
from bullet_admin.utils import get_allowed_countries
from bullet_admin.views.generic.links import DeleteIcon, EditIcon, Link, ViewIcon


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


class OrderedSearch(MixinProtocol):
    def apply_search_filter(self, qs):
        search = self.request.GET.get("q")
        if not search:
            return qs

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

    def apply_ordering(self, qs):
        order_by = self.request.GET.get("order_by")
        if order_by:
            return qs.order_by(order_by)
        return qs


class GenericList(CountryNavigation, LanguageNavigation, OrderedSearch, MixinProtocol):
    template_name = "bullet_admin/generic/list.html"
    paginate_by = 100
    list_title: str | None = None
    list_subtitle: str | None = None
    list_links: list[Link] = []

    table_fields: list[str] = []
    table_labels: dict[str, str] = {}
    table_field_templates: dict[str, str] = {}

    # deprecated
    object_name = None

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = {}
        qs = self.get_queryset()
        if object_list:
            qs = object_list

        qs = self.apply_country_filter(qs)
        qs = self.apply_language_filter(qs)
        qs = self.apply_ordering(qs)
        ctx["count"] = qs.count()  # count before searching
        qs = self.apply_search_filter(qs)

        ctx.update(super().get_context_data(object_list=qs, **kwargs))

        ctx["object_name"] = self.get_object_name()

        OLD_NAMES = [
            "help_url",
            "create_url",
            "upload_url",
            "export_url",
            "new_folder_url",
            "assign_numbers_url",
        ]
        for name in OLD_NAMES:
            val = getattr(self, name, None)
            ctx[name] = val
            if val:
                warnings.warn(f"{name} is deprecated in {self.__class__.__name__}.")

        # NEW
        ctx["list_title"] = self.get_list_title()
        ctx["list_subtitle"] = self.get_list_subtitle()
        ctx["list_links"] = self.get_list_links()

        ctx["table_labels"] = self.get_table_labels()
        ctx["table_rows"] = map(self.get_row_context, ctx["object_list"])

        return ctx

    @cached_property
    def get_model(self):  # type: ignore
        return self.model if self.model else self.get_queryset().model

    def get_list_title(self):
        if self.list_title:
            return self.list_title
        return self.get_model()._meta.verbose_name_plural.capitalize()

    def get_list_links(self) -> list[Link]:
        return self.list_links

    def get_list_subtitle(self) -> str | None:
        # TODO: Remove
        if hasattr(self, "subtitle"):
            warnings.warn(f"subtitle is deprecated in {self.__class__.__name__}")
            return self.subtitle
        return self.list_subtitle

    def get_table_fields(self) -> list[str]:
        # TODO: Remove
        if hasattr(self, "get_fields"):
            warnings.warn(f"get_fields is deprecated in {self.__class__.__name__}")
            return self.get_fields()
        if hasattr(self, "fields"):
            warnings.warn(f"fields is deprecated in {self.__class__.__name__}")
            return self.fields
        return self.table_fields

    def get_object_name(self):
        return (
            self.object_name
            if self.object_name
            else self.get_list_title().split(" ")[-1].lower()[0:-1]
        )

    def get_table_labels(self) -> list[tuple[str, str]]:
        # TODO: Remove
        if hasattr(self, "get_labels"):
            warnings.warn(f"get_labels is deprecated in {self.__class__.__name__}")
            return self.get_labels()

        labels = []
        for field in self.get_table_fields():
            label = field.replace("_", " ").capitalize()
            if field in self.table_labels:
                label = self.table_labels[field]

            labels.append((label, field))

        return labels

    def _migrate_old_links(self, object):
        # TODO: Remove
        links = []
        MAPPING = {
            "get_edit_url": EditIcon,
            "get_view_url": ViewIcon,
            "get_delete_url": DeleteIcon,
            "get_download_url": None,
            "get_generate": None,
        }

        for func, icon in MAPPING.items():
            if hasattr(self, func):
                warnings.warn(f"{func} is deprecated in {self.__class__.__name__}")
                if not icon:
                    continue
                url = getattr(self, func)(object)
                links.append(icon(url))

        return links

    def get_row_links(self, object) -> list[Link]:
        return self._migrate_old_links(object)

    def get_row_fields(self, object) -> list[str]:
        if hasattr(self, "field_templates"):
            warnings.warn(f"field_templates is deprecated in {self.__class__.__name__}")
            self.table_field_templates = self.field_templates

        fields = []
        for field in self.get_table_fields():
            data = getattr(object, field, None)

            if field in self.table_field_templates:
                data = mark_safe(
                    render_to_string(
                        self.table_field_templates[field], {"object": object}
                    )
                )

            fn_name = f"get_{field}_content"
            if hasattr(self, fn_name):
                data = getattr(self, fn_name)(object)

            fields.append(data)
        return fields

    def get_row_context(self, object):
        # TODO: Remove
        if hasattr(self, "create_row"):
            warnings.warn(f"create_row is deprecated in {self.__class__.__name__}")

        return {
            "fields": self.get_row_fields(object),
            "links": self.get_row_links(object),
        }
