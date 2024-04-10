from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django_htmx.http import HTMX_STOP_POLLING
from documents.models import TexJob

from bullet_admin.forms.tex import LetterCallbackForm


@method_decorator(csrf_exempt, name="dispatch")
class LetterCallbackView(View):
    def post(self, *args, **kwargs):
        job = get_object_or_404(TexJob, pk=kwargs["id"], output_file="")

        form = LetterCallbackForm(self.request.POST, self.request.FILES)
        if not form.is_valid():
            print(form.errors)
            return HttpResponse("invalid data", status=400)

        job.output_log = form.cleaned_data.get("tectonic_output", "")
        job.output_file = form.cleaned_data.get("file", "")
        job.output_error = form.cleaned_data.get("error", "")
        job.completed = True
        job.save()

        return HttpResponse("ok")


class JobDetailView(LoginRequiredMixin, DetailView):
    require_unlocked_competition = False

    def get_queryset(self):
        return TexJob.objects.filter(Q(creator=self.request.user) | Q(creator=None))

    def render_to_response(self, context, **response_kwargs):
        resp = super().render_to_response(context, **response_kwargs)

        if self.request.htmx and self.object.completed:
            resp.status_code = HTMX_STOP_POLLING

        return resp

    def get_template_names(self):
        if self.request.htmx:
            return ["bullet_admin/tex/job_output.html"]
        return ["bullet_admin/tex/job.html"]
