from bullet.views import FormAndFormsetMixin
from competitions.models import Competition
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import get_language_info
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView
from web.models import ContentBlock, Menu, Page, PageBlock

from bullet_admin.access import PermissionCheckMixin, is_country_admin
from bullet_admin.forms.content import (
    ContentBlockForm,
    ContentBlockWithRefForm,
    MenuItemForm,
    PageBlockCreateForm,
    PageBlockUpdateForm,
    PageCopyForm,
    PageForm,
)
from bullet_admin.mixins import (
    MixinProtocol,
    RedirectBackMixin,
)
from bullet_admin.utils import get_active_branch
from bullet_admin.views import DeleteView as BDeleteView
from bullet_admin.views import GenericDeleteView, GenericForm
from bullet_admin.views.generic.links import (
    DeleteIcon,
    EditIcon,
    ExternalViewIcon,
    Link,
    NewLink,
)
from bullet_admin.views.generic.list import GenericList


class PageQuerySetMixin(MixinProtocol):
    def get_queryset(self):
        return Page.objects.filter(branch=get_active_branch(self.request)).order_by(
            "slug", "language"
        )


class PageListView(PermissionCheckMixin, PageQuerySetMixin, GenericList, ListView):
    required_permissions = [is_country_admin]
    list_links = [NewLink("page", reverse_lazy("badmin:page_create"))]

    table_labels = {"slug": "URL"}
    table_fields = ["title", "slug", "language", "countries"]
    table_field_templates = {
        "countries": "bullet_admin/content/field__countries.html",
    }

    def get_language_content(self, obj):
        lang = get_language_info(obj.language)
        return lang["name"]

    def get_row_links(self, obj) -> list[Link]:
        view = reverse(
            "page",
            kwargs={
                "b_country": obj.countries[0].lower(),
                "b_language": obj.language,
                "slug": obj.slug,
            },
        )

        return [
            EditIcon(reverse("badmin:page_edit", args=[obj.pk])),
            ExternalViewIcon(view),
            DeleteIcon(reverse("badmin:page_delete", args=[obj.pk])),
        ]


class PageCopyView(PermissionCheckMixin, PageQuerySetMixin, GenericForm, FormView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/page_copy.html"
    form_title = "Copy content"
    form_class = PageCopyForm

    @cached_property
    def page(self):
        return get_object_or_404(self.get_queryset(), id=self.kwargs["page_id"])

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["page_qs"] = self.get_queryset()
        return kw

    @transaction.atomic
    def form_valid(self, form):
        source: Page = form.cleaned_data["page"]
        dest: Page = self.page

        dest.content = source.content
        dest.save()

        dest.pageblock_set.get_queryset().delete()

        for block in source.pageblock_set.all():
            new_block = PageBlock()
            new_block.page = dest
            new_block.data = block.data
            new_block.order = block.order
            new_block.block_type = block.block_type
            new_block.states = block.states
            new_block.save()

        return HttpResponseRedirect(reverse("badmin:page_edit", kwargs={"pk": dest.id}))


class PageEditView(
    PermissionCheckMixin,
    PageQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    UpdateView,
):
    required_permissions = [is_country_admin]
    form_class = PageForm
    template_name = "bullet_admin/content/page_edit.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = get_active_branch(self.request)
        return kw

    def get_default_success_url(self):
        return reverse("badmin:page_list")


class PageCreateView(
    PermissionCheckMixin,
    PageQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    CreateView,
):
    required_permissions = [is_country_admin]
    form_title = "Create page"
    form_class = PageForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = get_active_branch(self.request)
        return kw

    def get_initial(self):
        initial = super().get_initial()
        if "language" not in initial:
            initial["language"] = self.request.GET.get("language", None)
        return initial

    def get_default_success_url(self):
        return reverse("badmin:page_list")

    def form_valid(self, form):
        page = form.save(commit=False)
        page.branch = get_active_branch(self.request)
        page.save()

        return HttpResponseRedirect(self.get_success_url())


class PageDeleteView(
    PermissionCheckMixin, PageQuerySetMixin, RedirectBackMixin, DeleteView
):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/page_delete.html"

    def get_default_success_url(self):
        return reverse("badmin:page_list")


class PageBlockListView(PermissionCheckMixin, ListView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/page_block_list.html"

    def get_queryset(self):
        return PageBlock.objects.filter(page_id=self.kwargs["page_id"])

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["page"] = get_object_or_404(Page, id=self.kwargs["page_id"])
        ctx["states"] = Competition.State
        return ctx


class PageBlockUpdateView(
    PermissionCheckMixin, FormAndFormsetMixin, GenericForm, FormView
):
    required_permissions = [is_country_admin]
    form_title = "Page block content"

    @cached_property
    def page_block(self):
        return get_object_or_404(
            PageBlock,
            page_id=self.kwargs["page_id"],
            id=self.kwargs["pk"],
        )

    def get_form_class(self):
        return self.page_block.block.form

    def get_formset_class(self):
        return self.page_block.block.formset

    def save_forms(self, form, formset):
        block = self.page_block
        if block.data is None:
            block.data = {}  # type:ignore
        block.data.update(form.cleaned_data)
        if formset is not None:
            items = []
            for form in formset:
                if not form.cleaned_data or form.cleaned_data["DELETE"]:
                    continue
                data = form.cleaned_data
                del data["DELETE"]
                items.append(data)
            items.sort(key=lambda x: x.get("ORDER") or 0)
            block.data["items"] = items
        block.save()

    def get_initial(self):  # type:ignore
        return self.page_block.data

    def get_formset_kwargs(self):
        kw = super().get_formset_kwargs()
        if self.page_block.data and "items" in self.page_block.data:
            kw["initial"] = self.page_block.data["items"]
        return kw

    def get_success_url(self):
        return reverse(
            "badmin:page_block_list", kwargs={"page_id": self.kwargs["page_id"]}
        )


class PageBlockSettingsView(PermissionCheckMixin, GenericForm, UpdateView):
    required_permissions = [is_country_admin]
    form_title = "Page block settings"
    form_class = PageBlockUpdateForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            PageBlock,
            page_id=self.kwargs["page_id"],
            id=self.kwargs["pk"],
        )

    def get_success_url(self):
        return reverse(
            "badmin:page_block_list", kwargs={"page_id": self.kwargs["page_id"]}
        )


class PageBlockCreateView(PermissionCheckMixin, GenericForm, CreateView):
    required_permissions = [is_country_admin]
    form_title = "New page block"
    form_class = PageBlockCreateForm

    def get_success_url(self):
        return reverse(
            "badmin:page_block_update",
            kwargs={"page_id": self.kwargs["page_id"], "pk": self.object.id},
        )

    def form_valid(self, form):
        self.object = block = form.save(commit=False)
        block.page = get_object_or_404(Page, id=self.kwargs["page_id"])
        block.save()

        return HttpResponseRedirect(self.get_success_url())


class PageBlockDeleteView(PermissionCheckMixin, DeleteView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/page_block_delete.html"

    def get_object(self, queryset=None):
        return get_object_or_404(
            PageBlock,
            page_id=self.kwargs["page_id"],
            id=self.kwargs["pk"],
        )

    def get_success_url(self):
        return reverse(
            "badmin:page_block_list", kwargs={"page_id": self.kwargs["page_id"]}
        )


class ContentBlockQuerySetMixin(MixinProtocol):
    def get_queryset(self):
        return ContentBlock.objects.filter(
            branch=get_active_branch(self.request)
        ).order_by("group", "reference", "language")


class ContentBlockListView(PermissionCheckMixin, ListView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/contentblock_list.html"
    paginate_by = 50

    def get_queryset(self):  # type:ignore
        return (
            ContentBlock.objects.filter(
                Q(branch=get_active_branch(self.request)) | Q(branch__isnull=True)
            )
            .values("group", "reference")
            .distinct()
        )


class ContentBlockTranslationListView(PermissionCheckMixin, ListView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/contentblock_trans.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super(ContentBlockTranslationListView, self).get_context_data(
            *args, **kwargs
        )
        ctx["group"] = self.kwargs["group"]
        ctx["reference"] = self.kwargs["reference"]
        return ctx

    def get_queryset(self):
        return (
            ContentBlock.objects.filter(
                Q(branch=get_active_branch(self.request)) | Q(branch__isnull=True)
            )
            .filter(group=self.kwargs["group"], reference=self.kwargs["reference"])
            .order_by("branch", "language", "country")
        )


class ContentBlockEditView(PermissionCheckMixin, ContentBlockQuerySetMixin, UpdateView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/contentblock_form.html"
    form_class = ContentBlockForm
    object: ContentBlock

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = get_active_branch(self.request)
        return kw

    def get_success_url(self):
        return reverse(
            "badmin:contentblock_trans",
            kwargs={"group": self.object.group, "reference": self.object.reference},
        )


class ContentBlockDeleteView(
    PermissionCheckMixin, ContentBlockQuerySetMixin, BDeleteView
):
    required_permissions = [is_country_admin]
    object: ContentBlock

    def get_success_url(self):
        return reverse(
            "badmin:contentblock_trans",
            kwargs={"group": self.object.group, "reference": self.object.reference},
        )


class ContentBlockCreateView(
    PermissionCheckMixin, ContentBlockQuerySetMixin, CreateView
):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/contentblock_form.html"
    form_class = ContentBlockWithRefForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = get_active_branch(self.request)
        return kw

    def get_initial(self):
        return {
            "group": self.request.GET.get("group"),
            "reference": self.request.GET.get("reference"),
        }

    def form_valid(self, form):
        content_block = form.save(commit=False)
        content_block.branch = get_active_branch(self.request)
        content_block.save()

        return HttpResponseRedirect(
            reverse(
                "badmin:contentblock_trans",
                kwargs={
                    "group": content_block.group,
                    "reference": content_block.reference,
                },
            )
        )


class MenuItemListView(PermissionCheckMixin, GenericList, ListView):
    required_permissions = [is_country_admin]
    list_links = [NewLink("menu item", reverse_lazy("badmin:menu_create"))]

    table_labels = {"url": "URL"}
    table_fields = ["title", "url", "order", "language", "countries"]
    table_field_templates = {
        "countries": "bullet_admin/content/field__countries.html",
    }

    def get_queryset(self):
        return Menu.objects.filter(branch=get_active_branch(self.request)).order_by(
            "language", "order"
        )

    def get_language_content(self, obj):
        lang = get_language_info(obj.language)
        return lang["name"]

    def get_row_links(self, obj) -> list[Link]:
        return [
            EditIcon(reverse("badmin:menu_edit", args=[obj.pk])),
            DeleteIcon(reverse("badmin:menu_delete", args=[obj.pk])),
        ]


class MenuItemUpdateView(PermissionCheckMixin, UpdateView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/menu_form.html"
    form_class = MenuItemForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = get_active_branch(self.request)
        return kw

    def get_queryset(self):
        return Menu.objects.filter(branch=get_active_branch(self.request))

    def get_success_url(self):
        return reverse("badmin:menu_list")


class MenuItemCreateView(PermissionCheckMixin, CreateView):
    required_permissions = [is_country_admin]
    template_name = "bullet_admin/content/menu_form.html"
    form_class = MenuItemForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = get_active_branch(self.request)
        return kw

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.branch = get_active_branch(self.request)
        obj.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("badmin:menu_list")


class MenuItemDeleteView(PermissionCheckMixin, RedirectBackMixin, GenericDeleteView):
    required_permissions = [is_country_admin]
    model = Menu
