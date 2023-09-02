from countries.views import CountryDetectView, CountrySelectView
from django.conf import settings
from django.conf.urls.static import static
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
                path("", include("problems.urls")),
                path("", include("gallery.urls")),
                path("admin/", views.AdminRedirectView.as_view()),
                path("<slug>/", page.PageView.as_view(), name="page"),
            ]
        ),
    ),
]

handler404 = "web.views.error_404_view"

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
