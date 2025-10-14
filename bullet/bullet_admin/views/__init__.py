from competitions.models import Competition
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.views.generic import TemplateView
from django.views.generic.edit import BaseDeleteView
from django.views.generic.edit import DeleteView as DjDeleteView
from django_htmx.http import HttpResponseClientRefresh

from bullet_admin.mixins import MixinProtocol
from bullet_admin.models import CompetitionRole
from bullet_admin.utils import get_active_competition
from bullet_admin.views.generic.list import GenericList  # noqa


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


class GenericDeleteView(DjDeleteView):
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
