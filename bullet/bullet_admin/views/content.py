from bullet_admin.forms.content import PageForm
from bullet_admin.mixins import TranslatorRequiredMixin
from bullet_admin.views import DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from web.models import Page


class PageQuerySetMixin:
    def get_queryset(self):
        return Page.objects.filter(branch=self.request.BRANCH).order_by("slug").all()


class PageListView(TranslatorRequiredMixin, PageQuerySetMixin, ListView):
    template_name = "bullet_admin/content/page_list.html"
    paginate_by = 100


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
