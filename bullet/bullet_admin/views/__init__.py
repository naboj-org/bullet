from operator import attrgetter

from competitions.models import Competition
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Func, Q
from django.http import HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django.views.generic.edit import BaseDeleteView
from django_htmx.http import HttpResponseClientRefresh

from bullet_admin.models import CompetitionRole
from bullet_admin.utils import get_active_competition, get_allowed_countries


class DeleteView(BaseDeleteView):
    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=["POST"])


class GenericForm:
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


class GenericDelete:
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


class GenericList:
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
        qs = self.get_country_queryset(qs)
        qs = self.get_language_queryset(qs)
        qs = self.get_orderby_queryset(qs)
        ctx["count"] = qs.count()
        qs = self.get_search_queryset(qs)

        ctx |= super().get_context_data(object_list=qs, **kwargs)

        ctx["countries"] = self.country_navigation()
        ctx["languages"] = self.language_navigation()
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

    def get_country_queryset(self, qs):
        country = self.request.GET.get("country")
        fields = list(map(attrgetter("name"), self.get_model()._meta.get_fields()))

        if country:
            if "country" in fields:
                qs = qs.filter(country=country)
            elif "countries" in fields:
                qs = qs.filter(countries__contains=[country]) | qs.filter(countries=[])
            elif "team_countries" in fields:
                qs = qs.filter(team_countries__contains=[country]) | qs.filter(
                    team_countries=[]
                )

        allowed_countries = get_allowed_countries(self.request)
        if allowed_countries is not None:
            if "country" in fields:
                qs = qs.filter(country__in=allowed_countries)
            elif "countries" in fields:
                qs = qs.filter(countries__contains=allowed_countries) | qs.filter(
                    countries=[]
                )
            elif "team_countries" in fields:
                qs = qs.filter(team_countries__contains=allowed_countries) | qs.filter(
                    team_countries=[]
                )
        return qs

    def country_navigation(self):
        allowed_countries = get_allowed_countries(self.request)
        countries = self.get_queryset()
        fields = list(map(attrgetter("name"), self.get_model()._meta.get_fields()))

        if "country" in fields:
            pass
        elif "countries" in fields:
            countries = countries.annotate(
                country=Func(F("countries"), function="unnest")
            )
        elif "team_countries" in fields:
            countries = countries.annotate(
                country=Func(F("team_countries"), function="unnest")
            )
        else:
            return None

        countries = (
            countries.values_list("country", flat=True).order_by("country").distinct()
        )

        if allowed_countries is not None:
            countries = countries.filter(country__in=allowed_countries)

        if countries.count() <= 1:
            return None
        return countries

    def get_language_queryset(self, qs):
        language = self.request.GET.get("language")
        if language:
            fields = list(map(attrgetter("name"), self.get_model()._meta.get_fields()))

            if "language" in fields:
                qs = qs.filter(language=language)
            elif "languages" in fields:
                qs = qs.filter(languages__contains=[language]) | qs.filter(languages=[])
            elif "team_languages" in fields:
                qs = qs.filter(team_languages__contains=[language]) | qs.filter(
                    team_languages=[]
                )
            elif "accepted_languages" in fields:
                qs = qs.filter(accepted_languages__contains=[language]) | qs.filter(
                    accepted_languages=[]
                )

        return qs

    def language_navigation(self):
        languages = self.get_queryset()
        fields = list(map(attrgetter("name"), self.get_model()._meta.get_fields()))

        if "language" in fields:
            languages = languages
        elif "languages" in fields:
            languages = languages.annotate(
                language=Func(F("languages"), function="unnest")
            )
        elif "team_languages" in fields:
            languages = languages.annotate(
                language=Func(F("team_languages"), function="unnest")
            )
        elif "accepted_languages" in fields:
            languages = languages.annotate(
                language=Func(F("accepted_languages"), function="unnest")
            )
        else:
            return None

        languages = (
            languages.values_list("language", flat=True).order_by("language").distinct()
        )

        if languages.count() <= 1:
            return None
        return languages

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
            request.session[f"badmin_{request.BRANCH.identifier}_competition"] = (
                request.GET.get("competition")
            )
        return HttpResponseClientRefresh()
