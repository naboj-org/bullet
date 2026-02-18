from django.core.files.storage import default_storage
from django.utils.translation import get_language
from django.views.generic import ListView
from problems.models import ProblemStatement

from competitions.models import Competition


class ArchiveListView(ListView):
    template_name = "archive/list.html"

    def get_queryset(self):
        return Competition.objects.for_user(
            self.request.user, self.request.BRANCH
        ).prefetch_related("albums")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        qs = (
            ProblemStatement.objects.filter(problem__competition__in=ctx["object_list"])
            .values_list("problem__competition", flat=True)
            .distinct()
        )

        ctx["native"] = list(qs.filter(language=get_language()))
        ctx["english"] = list(qs.filter(language="en"))
        ctx["slovak"] = list(qs.filter(language="sk"))
        ctx["czech"] = list(qs.filter(language="cs"))

        for competition in ctx["object_list"]:
            if default_storage.exists(
                competition.secret_dir / f"problems-{get_language()}.pdf"
            ):
                ctx["native"].append(competition.id)
            if default_storage.exists(competition.secret_dir / "problems-en.pdf"):
                ctx["english"].append(competition.id)
            if default_storage.exists(competition.secret_dir / "problems-sk.pdf"):
                ctx["slovak"].append(competition.id)
            if default_storage.exists(competition.secret_dir / "problems-cs.pdf"):
                ctx["czech"].append(competition.id)

        return ctx
