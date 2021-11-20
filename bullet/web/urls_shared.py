from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
]

branch_shared_patterns = [
    ('', views.HomepageView, 'homepage'),
    ('register/<category>/', views.RegistrationView, 'registration'),
    ('confirm_registration/<secret_link>/', views.RegistrationConfirmView, 'registration_confirm'),
    ('edit_team/<secret_link>/', views.TeamEditView, 'team_edit'),
    ('teams/', views.TeamList, 'teams'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns

