from countries.views import CountryDetectView, CountrySelectView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import include, path, re_path
from web import views
from web.views import page

urlpatterns = [
    path("", CountryDetectView.as_view()),
    path("country_selector/", CountrySelectView.as_view(), name="country_selector"),
    path("admin/", include("bullet_admin.urls")),
    re_path(
        r"^(?P<b_country>[a-z]{2})/(?P<b_language>[a-z\-]+)/",
        include(
            [
                path("", views.HomepageView.as_view(), name="homepage"),
                path("", include("competitions.urls")),
                # path(
                #     "confirm_registration/<secret_link>/",
                #     registration.RegistrationConfirmView.as_view(),
                #     name="registration_confirm",
                # ),
                # path("teams/", teams.TeamList.as_view(), name="teams"),
                path("admin/", lambda r: redirect("/admin/")),
                path("<slug>/", page.PageView.as_view(), name="page"),
            ]
        ),
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
