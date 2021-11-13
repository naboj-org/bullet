from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from web import views

urlpatterns = [
    path('admin/', admin.site.urls)
]

branch_shared_patterns = [
    (r'^$', views.HomepageView, 'homepage'),
    (r'^register/(?P<category>\d)/$', views.RegistrationView, 'registration'),
    (r'^confirm_registration/(?P<secret_link>\w{48})/$', views.RegistrationConfirmView, 'registration_confirm'),
    (r'^edit_team/(?P<secret_link>\w{48})/$', views.TeamEditView, 'team_edit'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
