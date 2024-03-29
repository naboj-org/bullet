from django.views.generic import ListView

from competitions.models import Competition


class ArchiveListView(ListView):
    template_name = "archive/list.html"

    def get_queryset(self):
        return Competition.objects.for_user(
            self.request.user, self.request.BRANCH
        ).prefetch_related("albums")
