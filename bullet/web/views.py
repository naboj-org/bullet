from django.views.generic import TemplateView

from competitions.models import Competition


class BranchSpecificViewMixin:
    branch: Competition.Branch = None


class HomepageView(TemplateView, BranchSpecificViewMixin):
    template_name = 'web/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branch'] = self.branch
        return context
