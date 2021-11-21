from competitions.models import Competition
from django.utils import timezone
from django.views.generic import TemplateView


class BranchViewMixin:
    branch: Competition.Branch = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["branch"] = self.branch
        return ctx


class HomepageView(BranchViewMixin, TemplateView):
    template_name = "web/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context[
                "open_competition"
            ] = Competition.objects.currently_running_registration().get(
                branch=self.branch
            )
            context["registration_open_for"] = (
                context["open_competition"].registration_end - timezone.now()
            )
        except Competition.DoesNotExist:
            pass

        return context
