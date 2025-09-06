from django.views.generic import ListView
from django.utils.translation import get_language
from django.core.files.storage import default_storage

from competitions.models import Competition

from problems.models import ProblemStatement

class ArchiveListView(ListView):
    template_name = "archive/list.html"

    def get_queryset(self):
        return Competition.objects.for_user(
            self.request.user, self.request.BRANCH
        ).prefetch_related("albums")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
            	
        ctx["native"] = list(ProblemStatement.objects.filter(
            problem__competition__in=ctx["object_list"], language=get_language()
        )
        .values_list("problem__competition", flat=True)
        .distinct())
        ctx["english"] = list(ProblemStatement.objects.filter(
            problem__competition__in=ctx["object_list"], language="en"
        )
        .values_list("problem__competition", flat=True)
        .distinct())
        ctx["slovak"] = list(ProblemStatement.objects.filter(
            problem__competition__in=ctx["object_list"], language="sk"
        )
        .values_list("problem__competition", flat=True)
        .distinct())
        ctx["czech"] = list(ProblemStatement.objects.filter(
            problem__competition__in=ctx["object_list"], language="cs"
        )
        .values_list("problem__competition", flat=True)
        .distinct())
        
        for competition in ctx["object_list"]:
            if default_storage.exists(competition.secret_dir / f"problems-{get_language()}.pdf"):
            	ctx["native"].append(competition.id)
            if default_storage.exists(competition.secret_dir / f"problems-en.pdf"):
            	ctx["english"].append(competition.id)
            if default_storage.exists(competition.secret_dir / f"problems-sk.pdf"):
            	ctx["slovak"].append(competition.id)
            if default_storage.exists(competition.secret_dir / f"problems-cs.pdf"):
            	ctx["czech"].append(competition.id)
       	
        return ctx
