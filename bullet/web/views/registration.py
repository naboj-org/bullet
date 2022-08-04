from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from users.models import Team


class RegistrationConfirmView(TemplateView):
    template_name = "web/registration_confirm.html"

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        secret_link = kwargs.pop("secret_link")

        try:
            team = Team.objects.select_related(
                "competition_venue__category_competition__competition"
            ).get(secret_link=secret_link)
            if team.confirmed_at is not None:
                return redirect("team_edit", secret_link=secret_link)
            else:
                team.confirmed_at = timezone.now()
                team.save(update_fields=("confirmed_at",))
                error = None

        except Team.DoesNotExist:
            error = _("Confirmation link is invalid")

        # TODO forbid confirmation if the registration
        #  is not running/capacity has been filled
        context = self.get_context_data(**kwargs)
        context["error"] = error

        return self.render_to_response(context)
