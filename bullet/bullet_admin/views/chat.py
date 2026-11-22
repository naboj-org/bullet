from urllib.parse import urlencode

from django.conf import settings
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from bullet_admin.access import PermissionCheckMixin, is_operator
from bullet_admin.chat import generate_chat_login_jwt
from bullet_admin.utils import get_active_competition


@method_decorator(never_cache, name="dispatch")
class ChatLoginView(PermissionCheckMixin, View):
    required_permissions = [is_operator]
    http_method_names = ["get"]

    def get_permission_competition(self):
        competition = get_active_competition(self.request)
        if competition is None:
            raise Http404("No active competition.")
        return competition

    def permission_denied_response(self):
        return JsonResponse({"error": "Chat access denied."}, status=403)

    def get_token(self):
        return generate_chat_login_jwt(
            self.get_permission_competition(), self.request.user
        )

    def get(self, request, *args, **kwargs):
        query = urlencode({"token": self.get_token()})
        response = HttpResponseRedirect(
            f"{settings.ORGCHAT_URL.rstrip('/')}/api/auth?{query}"
        )
        response["Referrer-Policy"] = "no-referrer"
        return response


class ChatTokenView(ChatLoginView):
    """Same-origin endpoint for the widget's asynchronous getToken hook."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"token": self.get_token()})
