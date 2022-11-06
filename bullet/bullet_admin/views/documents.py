from bullet_admin.forms.documents import CertificateForm
from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.views.generic import FormView
from documents.generators.certificate import certificates_for_venue


class CertificateView(AdminRequiredMixin, FormView):
    form_class = CertificateForm
    template_name = "bullet_admin/documents/certificates.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        venue = form.cleaned_data["venue"]

        if not can_access_venue(self.request, venue):
            raise PermissionDenied()

        template = form.cleaned_data["template"]
        data = certificates_for_venue(venue, template)
        return FileResponse(data, as_attachment=True, filename="certificates.pdf")
