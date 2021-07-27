from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns

from competitions.models import Competition
from .urls_shared import urlpatterns as shared_patterns
from .urls_shared import branch_shared_patterns

urlpatterns = i18n_patterns(
    *(shared_patterns + [
        url(path, view.as_view(branch=Competition.Branch.MATH), name=name)
        for path, view, name in branch_shared_patterns
    ] + [
        # Any branch specific patterns
    ])
)
