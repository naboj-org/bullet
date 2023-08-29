from bullet_admin.forms.documents import CertificateForm, TeamListForm
from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import get_active_competition
from django.http import FileResponse
from django.views.generic import FormView
from documents.generators.certificate import certificates_for_venue
from documents.generators.team_list import team_list
from users.models import Team


class CertificateView(AdminRequiredMixin, FormView):
    form_class = CertificateForm
    template_name = "bullet_admin/documents/certificates.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        data = certificates_for_venue(
            form.cleaned_data["venue"],
            form.cleaned_data["template"],
            form.cleaned_data["count"],
            form.cleaned_data["empty"],
        )
        return FileResponse(data, as_attachment=True, filename="certificates.pdf")


class TeamListView(AdminRequiredMixin, FormView):
    form_class = TeamListForm
    template_name = "bullet_admin/documents/team_list.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        venue = form.cleaned_data["venue"]
        data = team_list(
            Team.objects.competing().filter(venue=venue, number__isnull=False),
            f"Team list: {venue.name}",
        )
        return FileResponse(data, as_attachment=True, filename="team_list.pdf")
