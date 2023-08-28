from competitions.models import Competition
from django.views.generic import ListView


class ArchiveListView(ListView):
    template_name = "archive/list.html"

    def get_queryset(self):
        return Competition.objects.for_user(self.request.user, self.request.BRANCH)
