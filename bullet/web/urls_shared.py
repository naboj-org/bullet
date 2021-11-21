import web.views
import web.views.registration
import web.views.teams
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
]

branch_shared_patterns = [
    ("", web.views.HomepageView, "homepage"),
    ("register/<category>/", web.views.registration.RegistrationView, "registration"),
    (
        "confirm_registration/<secret_link>/",
        web.views.registration.RegistrationConfirmView,
        "registration_confirm",
    ),
    ("edit_team/<secret_link>/", web.views.teams.TeamEditView, "team_edit"),
    ("teams/", web.views.teams.TeamList, "teams"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
