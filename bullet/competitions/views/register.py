from competitions.models import CategoryCompetition, CategoryDescription, Competition
from django.views.generic import TemplateView
from users.forms.registration import CategorySelectForm


class CategorySelectView(TemplateView):
    template_name = "teams/register_category.html"
    form_class = CategorySelectForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.request
        competition = Competition.objects.get_current_competition(req.BRANCH)
        categories = (
            CategoryCompetition.objects.filter(
                competition=competition,
                competitionvenue__venue__country=req.COUNTRY_CODE.upper(),
            )
            .order_by("category__order")
            .select_related("category")
            .all()
        )
        descriptions = {
            d.category_id: d
            for d in CategoryDescription.objects.filter(
                category_id__in=[c.category_id for c in categories],
                countries__contains=[req.COUNTRY_CODE.upper()],
                language=req.LANGUAGE_CODE,
            )
        }
        ctx["categories"] = [
            {
                "category": c,
                "description": descriptions[c.category_id]
                if c.category_id in descriptions
                else None,
            }
            for c in categories
        ]
        return ctx
