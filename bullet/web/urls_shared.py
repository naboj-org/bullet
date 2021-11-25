from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from web import views
from web.views import page, registration, teams

urlpatterns = [
    path("admin/", admin.site.urls),
]

branch_shared_patterns = [
    ("", views.HomepageView, "homepage"),
    ("register/<category>/", registration.RegistrationView, "registration"),
    (
        "confirm_registration/<secret_link>/",
        registration.RegistrationConfirmView,
        "registration_confirm",
    ),
    ("edit_team/<secret_link>/", teams.TeamEditView, "team_edit"),
    ("teams/", teams.TeamList, "teams"),
    ("<url>/", page.PageView, "page"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
