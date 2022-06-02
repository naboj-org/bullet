from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from web import views
from web.views import page, registration, teams

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", views.HomepageView.as_view(), name="homepage"),
    path(
        "register/<category>/",
        registration.RegistrationView.as_view(),
        name="registration",
    ),
    path(
        "confirm_registration/<secret_link>/",
        registration.RegistrationConfirmView.as_view(),
        name="registration_confirm",
    ),
    path("edit_team/<secret_link>/", teams.TeamEditView.as_view(), name="team_edit"),
    path("teams/", teams.TeamList.as_view(), name="teams"),
    path("<url>/", page.PageView.as_view(), name="page"),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
