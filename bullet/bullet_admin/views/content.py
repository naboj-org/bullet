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

from bullet.views import FormAndFormsetMixin
from bullet_admin.forms.content import (
    ContentBlockForm,
    ContentBlockWithRefForm,
    MenuItemForm,
    PageBlockCreateForm,
    PageBlockUpdateForm,
    PageCopyForm,
    PageForm,
)
from bullet_admin.mixins import RedirectBackMixin, TranslatorRequiredMixin
from bullet_admin.views import DeleteView as BDeleteView
from bullet_admin.views import GenericDelete, GenericForm
from bullet_admin.views.generic.links import (
    DeleteIcon,
    EditIcon,
    ExternalViewIcon,
    Link,
    NewLink,
)
from bullet_admin.views.generic.list import GenericList


class PageQuerySetMixin:
    def get_queryset(self):
        return Page.objects.filter(branch=self.request.BRANCH).order_by(
            "slug", "language"
        )


class PageListView(TranslatorRequiredMixin, PageQuerySetMixin, GenericList, ListView):
    list_links = [NewLink("page", reverse_lazy("badmin:page_create"))]

    table_labels = {"slug": "URL"}
    table_fields = ["title", "slug", "language", "countries"]
    table_field_templates = {
        "countries": "bullet_admin/content/field__countries.html",
    }

    def get_language_content(self, object):
        lang = get_language_info(object.language)
        return lang["name"]

    def get_row_links(self, object) -> list[Link]:
        view = reverse(
            "page",
            kwargs={
                "b_country": object.countries[0].lower(),
                "b_language": object.language,
                "slug": object.slug,
            },
        )

        return [
            EditIcon(reverse("badmin:page_edit", args=[object.pk])),
            ExternalViewIcon(view),
            DeleteIcon(reverse("badmin:page_delete", args=[object.pk])),
        ]


class PageCopyView(TranslatorRequiredMixin, PageQuerySetMixin, GenericForm, FormView):
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
    TranslatorRequiredMixin,
    PageQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    UpdateView,
):
    form_class = PageForm
    template_name = "bullet_admin/content/page_edit.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_default_success_url(self):
        return reverse("badmin:page_list")


class PageCreateView(
    TranslatorRequiredMixin,
    PageQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    CreateView,
):
    form_title = "Create page"
    form_class = PageForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
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
        page.branch = self.request.BRANCH
        page.save()

        return HttpResponseRedirect(self.get_success_url())


class PageDeleteView(
    TranslatorRequiredMixin, PageQuerySetMixin, RedirectBackMixin, DeleteView
):
    template_name = "bullet_admin/content/page_delete.html"

    def get_default_success_url(self):
        return reverse("badmin:page_list")


class PageBlockListView(TranslatorRequiredMixin, ListView):
    template_name = "bullet_admin/content/page_block_list.html"

    def get_queryset(self):
        return PageBlock.objects.filter(page_id=self.kwargs["page_id"])

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["page"] = get_object_or_404(Page, id=self.kwargs["page_id"])
        ctx["states"] = Competition.State
        return ctx


class PageBlockUpdateView(
    TranslatorRequiredMixin, FormAndFormsetMixin, GenericForm, FormView
):
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
            block.data = {}
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

    def get_initial(self):
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


class PageBlockSettingsView(TranslatorRequiredMixin, GenericForm, UpdateView):
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


class PageBlockCreateView(TranslatorRequiredMixin, GenericForm, CreateView):
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


class PageBlockDeleteView(TranslatorRequiredMixin, DeleteView):
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


class ContentBlockQuerySetMixin:
    def get_queryset(self):
        return ContentBlock.objects.filter(branch=self.request.BRANCH).order_by(
            "group", "reference", "language"
        )


class ContentBlockListView(TranslatorRequiredMixin, ListView):
    template_name = "bullet_admin/content/contentblock_list.html"
    paginate_by = 50

    def get_queryset(self):
        return (
            ContentBlock.objects.filter(
                Q(branch=self.request.BRANCH) | Q(branch__isnull=True)
            )
            .values("group", "reference")
            .distinct()
        )


class ContentBlockTranslationListView(TranslatorRequiredMixin, ListView):
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
                Q(branch=self.request.BRANCH) | Q(branch__isnull=True)
            )
            .filter(group=self.kwargs["group"], reference=self.kwargs["reference"])
            .order_by("branch", "language", "country")
        )


class ContentBlockEditView(
    TranslatorRequiredMixin, ContentBlockQuerySetMixin, UpdateView
):
    template_name = "bullet_admin/content/contentblock_form.html"
    form_class = ContentBlockForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_success_url(self):
        return reverse(
            "badmin:contentblock_trans",
            kwargs={"group": self.object.group, "reference": self.object.reference},
        )


class ContentBlockDeleteView(
    TranslatorRequiredMixin, ContentBlockQuerySetMixin, BDeleteView
):
    def get_success_url(self):
        return reverse(
            "badmin:contentblock_trans",
            kwargs={"group": self.object.group, "reference": self.object.reference},
        )


class ContentBlockCreateView(
    TranslatorRequiredMixin, ContentBlockQuerySetMixin, CreateView
):
    template_name = "bullet_admin/content/contentblock_form.html"
    form_class = ContentBlockWithRefForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_initial(self):
        return {
            "group": self.request.GET.get("group"),
            "reference": self.request.GET.get("reference"),
        }

    def form_valid(self, form):
        content_block = form.save(commit=False)
        content_block.branch = self.request.BRANCH
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


class MenuItemListView(TranslatorRequiredMixin, GenericList, ListView):
    list_links = [NewLink("menu item", reverse_lazy("badmin:menu_create"))]

    table_labels = {"url": "URL"}
    table_fields = ["title", "url", "order", "language", "countries"]
    table_field_templates = {
        "countries": "bullet_admin/content/field__countries.html",
    }

    def get_queryset(self):
        return Menu.objects.filter(branch=self.request.BRANCH).order_by(
            "language", "order"
        )

    def get_language_content(self, object):
        lang = get_language_info(object.language)
        return lang["name"]

    def get_row_links(self, object) -> list[Link]:
        return [
            EditIcon(reverse("badmin:menu_edit", args=[object.pk])),
            DeleteIcon(reverse("badmin:menu_delete", args=[object.pk])),
        ]


class MenuItemEditView(TranslatorRequiredMixin, UpdateView):
    template_name = "bullet_admin/content/menu_form.html"
    form_class = MenuItemForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_queryset(self):
        return Menu.objects.filter(branch=self.request.BRANCH)

    def get_success_url(self):
        return reverse("badmin:menu_list")


class MenuItemCreateView(TranslatorRequiredMixin, CreateView):
    template_name = "bullet_admin/content/menu_form.html"
    form_class = MenuItemForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.branch = self.request.BRANCH.id
        obj.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("badmin:menu_list")


class MenuItemDeleteView(
    TranslatorRequiredMixin, RedirectBackMixin, GenericDelete, DeleteView
):
    model = Menu
