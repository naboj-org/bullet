from django.conf.urls import url

from competitions.models import Competition
from . import views
from .urls_shared import urlpatterns as shared_patterns

urlpatterns = shared_patterns + [
    url(r'^$', views.HomepageView.as_view(branch=Competition.Branch.PHYSICS), name='homepage'),
]
