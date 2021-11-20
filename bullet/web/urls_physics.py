from competitions.models import Competition
from django.conf.urls.i18n import i18n_patterns
from django.urls import path

from .urls_shared import branch_shared_patterns
from .urls_shared import urlpatterns as shared_patterns

urlpatterns = i18n_patterns(
    *(
        shared_patterns
        + [
            path(url, view.as_view(branch=Competition.Branch.PHYSICS), name=name)
            for url, view, name in branch_shared_patterns
        ]
        + [
            # Any branch specific patterns
        ]
    )
)
