from competitions.models import Competition
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from web.models import ContentBlock, Logo, Menu, Page, PageBlock

from bullet_admin.forms.content import (
    ContentBlockForm,
    ContentBlockWithRefForm,
    LogoForm,
    MenuItemForm,
    PageForm,
)
from bullet_admin.mixins import RedirectBackMixin, TranslatorRequiredMixin
from bullet_admin.views import DeleteView as BDeleteView
from bullet_admin.views import GenericForm


class PageQuerySetMixin:
    def get_queryset(self):
        return Page.objects.filter(branch=self.request.BRANCH).order_by(
            "slug", "language"
        )


class PageListView(TranslatorRequiredMixin, PageQuerySetMixin, ListView):
    template_name = "bullet_admin/content/page_list.html"
    paginate_by = 100

    def get_queryset(self):
        qs = super().get_queryset()
        if "language" in self.request.GET:
            qs = qs.filter(language=self.request.GET["language"])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["languages"] = (
            Page.objects.filter(branch=self.request.BRANCH)
            .values_list("language", flat=True)
            .distinct()
            .order_by("language")
        )
        return ctx


class PageEditView(
    TranslatorRequiredMixin,
    PageQuerySetMixin,
    RedirectBackMixin,
    GenericForm,
    UpdateView,
):
    form_title = "Edit page"
    form_class = PageForm

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


class LogoListView(TranslatorRequiredMixin, ListView):
    template_name = "bullet_admin/content/logo_list.html"

    def get_queryset(self):
        return Logo.objects.filter(branch=self.request.BRANCH)


class LogoEditView(TranslatorRequiredMixin, UpdateView):
    template_name = "bullet_admin/content/logo_form.html"
    form_class = LogoForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_queryset(self):
        return Logo.objects.filter(branch=self.request.BRANCH)

    def get_success_url(self):
        return reverse("badmin:logo_list")


class LogoCreateView(TranslatorRequiredMixin, CreateView):
    template_name = "bullet_admin/content/logo_form.html"
    form_class = LogoForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_success_url(self):
        return reverse("badmin:logo_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.branch = self.request.BRANCH.id
        obj.save()

        return HttpResponseRedirect(reverse("badmin:logo_list"))


class LogoDeleteView(TranslatorRequiredMixin, BDeleteView):
    def get_queryset(self):
        return Logo.objects.filter(branch=self.request.BRANCH)

    def get_success_url(self):
        return reverse("badmin:logo_list")


class MenuItemListView(TranslatorRequiredMixin, ListView):
    template_name = "bullet_admin/content/menu_list.html"

    def get_queryset(self):
        return Menu.objects.filter(branch=self.request.BRANCH).order_by(
            "language", "order"
        )


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


class MenuItemDeleteView(TranslatorRequiredMixin, BDeleteView):
    def get_queryset(self):
        return Menu.objects.filter(branch=self.request.BRANCH)

    def get_success_url(self):
        return reverse("badmin:menu_list")
