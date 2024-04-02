from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView

from bullet_admin.documentation import Access, get_page, get_pages
from bullet_admin.utils import get_active_competition


class DocumentationAccessMixin:
    def get_user_access(self) -> Access:
        access = Access(0)
        user = self.request.user
        competition = get_active_competition(self.request)

        brole = user.get_branch_role(self.request.BRANCH)
        if brole.is_admin:
            access |= Access.BRANCH

        crole = user.get_competition_role(competition)
        if crole.is_operator:
            access |= Access.OPERATOR
        if bool(crole.venues):
            access |= Access.VENUE
        if bool(crole.countries):
            access |= Access.COUNTRY

        return access


class DocumentationHomeView(LoginRequiredMixin, DocumentationAccessMixin, TemplateView):
    template_name = "bullet_admin/documentation/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pages = get_pages()
        access = self.get_user_access()
        pages = filter(lambda p: bool(p.access & access), pages)
        ctx["pages"] = pages
        return ctx


class DocumentationView(LoginRequiredMixin, DocumentationAccessMixin, TemplateView):
    template_name = "bullet_admin/documentation/page.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        page = get_page(kwargs["slug"])
        if not page:
            raise Http404()

        access = self.get_user_access()
        if not bool(page.access & access):
            raise Http404()

        ctx["page"] = page
        return ctx
