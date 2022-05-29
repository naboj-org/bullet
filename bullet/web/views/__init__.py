from competitions.models import Competition
from django.utils import timezone
from django.views.generic import TemplateView
from web.models import Organizer, Partner


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

        context["partners"] = Partner.objects.filter(branch=self.branch).all()
        context["organizers"] = Organizer.objects.filter(branch=self.branch).all()

        return context
