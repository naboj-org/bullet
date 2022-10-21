from bullet_admin.forms.emails import EmailCampaignForm
from bullet_admin.mixins import AnyAdminRequiredMixin
from bullet_admin.utils import get_active_competition
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from users.models import EmailCampaign


class CampaignListView(AnyAdminRequiredMixin, ListView):
    template_name = "bullet_admin/emails/list.html"

    def get_queryset(self):
        competition = get_active_competition(self.request)
        return EmailCampaign.objects.filter(competition=competition)


class CampaignCreateView(AnyAdminRequiredMixin, CreateView):
    form_class = EmailCampaignForm
    template_name = "bullet_admin/emails/form.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.competition = get_active_competition(self.request)
        obj.save()

        return HttpResponseRedirect(reverse("badmin:email_list"))


class CampaignUpdateView(AnyAdminRequiredMixin, UpdateView):
    form_class = EmailCampaignForm
    template_name = "bullet_admin/emails/form.html"

    def get_queryset(self):
        return EmailCampaign.objects.filter(
            competition=get_active_competition(self.request)
        )

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_success_url(self):
        return reverse("badmin:email_list")
