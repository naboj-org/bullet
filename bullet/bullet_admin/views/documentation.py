from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView
from users.models.organizers import User

from bullet_admin.access_v2 import (
    is_admin,
    is_branch_admin,
    is_country_admin,
    is_operator,
)
from bullet_admin.documentation import Access, get_page, get_pages
from bullet_admin.mixins import MixinProtocol
from bullet_admin.utils import get_active_competition


class DocumentationAccessMixin(MixinProtocol):
    def get_user_access(self) -> Access:
        access = Access(0)
        user = self.request.user
        assert isinstance(user, User)
        competition = get_active_competition(self.request)

        if is_branch_admin(user, competition):
            access |= Access.BRANCH
        if is_country_admin(user, competition):
            access |= Access.COUNTRY
        if is_admin(user, competition):
            access |= Access.VENUE
        if is_operator(user, competition):
            access |= Access.OPERATOR

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
