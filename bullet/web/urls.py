from countries.resolvers import country_patterns
from countries.views import CountryDetectView, CountrySelectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from web import views
from web.views import page, registration, teams

urlpatterns = [
    path("", CountryDetectView.as_view()),
    path("country_selector/", CountrySelectView.as_view(), name="country_selector"),
] + country_patterns(
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
