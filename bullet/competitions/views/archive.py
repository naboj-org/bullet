from competitions.models import Competition
from django.views.generic import ListView


class ArchiveListView(ListView):
    template_name = "archive/list.html"

    def get_queryset(self):
        return Competition.objects.filter(branch=self.request.BRANCH).order_by(
            "-web_start"
        )
