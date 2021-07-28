from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from web import views

urlpatterns = [
    path('admin/', admin.site.urls)
]

branch_shared_patterns = [
    (r'^$', views.HomepageView, 'homepage')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
