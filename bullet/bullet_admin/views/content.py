from bullet_admin.forms.content import (
    ContentBlockForm,
    ContentBlockWithRefForm,
    PageForm,
)
from bullet_admin.mixins import TranslatorRequiredMixin
from bullet_admin.views import DeleteView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from web.models import ContentBlock, Page


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
        if "q" in self.request.GET:
            qs = qs.filter(
                Q(title__icontains=self.request.GET["q"])
                | Q(slug__icontains=self.request.GET["q"])
            )
        return qs


class PageEditView(TranslatorRequiredMixin, PageQuerySetMixin, UpdateView):
    template_name = "bullet_admin/content/page_form.html"
    form_class = PageForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_success_url(self):
        return reverse("badmin:page_list")


class PageCreateView(TranslatorRequiredMixin, PageQuerySetMixin, CreateView):
    template_name = "bullet_admin/content/page_form.html"
    form_class = PageForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["create"] = True
        return ctx

    def get_success_url(self):
        return reverse("badmin:page_list")

    def form_valid(self, form):
        page = form.save(commit=False)
        page.branch = self.request.BRANCH
        page.save()

        return HttpResponseRedirect(self.get_success_url())


class PageDeleteView(TranslatorRequiredMixin, PageQuerySetMixin, DeleteView):
    def get_success_url(self):
        return reverse("badmin:page_list")


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
    TranslatorRequiredMixin, ContentBlockQuerySetMixin, DeleteView
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
