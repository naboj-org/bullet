from bullet_admin.forms.archive import ProblemImportForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from django.http import HttpResponse
from django.views.generic import FormView


# TODO: permissions
class ProblemImportView(GenericForm, FormView):
    form_class = ProblemImportForm
    template_name = "bullet_admin/archive/import.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        form.save()
        return HttpResponse("ok")
