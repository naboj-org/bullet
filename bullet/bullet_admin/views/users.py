from bullet_admin.forms.users import BranchRoleForm, CompetitionRoleForm, UserForm
from bullet_admin.mixins import DelegateRequiredMixin
from bullet_admin.models import BranchRole, CompetitionRole
from bullet_admin.utils import get_active_competition
from django.contrib import messages
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from users.emails.users import send_onboarding_email
from users.models import User


class UserListView(DelegateRequiredMixin, ListView):
    template_name = "bullet_admin/users/list.html"
    paginate_by = 50

    def get_queryset(self):
        branch_role = BranchRole.objects.filter(
            branch=self.request.BRANCH, user=OuterRef("pk")
        )
        competition_role = CompetitionRole.objects.filter(
            competition=get_active_competition(self.request), user=OuterRef("pk")
        )
        return User.objects.order_by("email").annotate(
            has_branch_role=Exists(branch_role),
            has_competition_role=Exists(competition_role),
        )


class UserCreateView(DelegateRequiredMixin, View):
    def get_forms(self, request):
        data = None
        if request.method == "POST":
            data = request.POST
        form = UserForm(data=data)
        bform = None
        cform = None

        brole = self.request.user.get_branch_role(self.request.BRANCH)
        if brole.is_admin:
            bform = BranchRoleForm(
                data=data,
            )

        competition = get_active_competition(self.request)
        crole = self.request.user.get_competition_role(competition)
        if brole.is_admin or crole.country or crole.venue:
            cform = CompetitionRoleForm(
                data=data,
                competition=competition,
                allowed_object=crole.country or crole.venue,
            )

        return form, bform, cform

    def get(self, request, *args, **kwargs):
        form, bform, cform = self.get_forms(request)

        return TemplateResponse(
            request,
            "bullet_admin/users/create.html",
            {"form": form, "bform": bform, "cform": cform},
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form, bform, cform = self.get_forms(request)

        if (
            not form.is_valid()
            or (bform and not bform.is_valid())
            or (cform and not cform.is_valid())
        ):
            return TemplateResponse(
                request,
                "bullet_admin/users/create.html",
                {"form": form, "bform": bform, "cform": cform},
            )

        user: User = form.save(commit=False)
        passwd = User.objects.make_random_password()
        user.set_password(passwd)
        user.save()

        brole = None
        if bform:
            brole = bform.save(commit=False)
            brole.user = user
            brole.branch = request.BRANCH
            brole.save()

        if cform and (not brole or not brole.is_admin):
            crole = cform.save(commit=False)
            crole.user = user
            crole.competition = get_active_competition(request)
            crole.save()

        send_onboarding_email(request.BRANCH, user, passwd)
        messages.success(request, "The user was created.")
        return HttpResponseRedirect(reverse("badmin:user_list"))
