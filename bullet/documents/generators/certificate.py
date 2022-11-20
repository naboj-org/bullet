import io

from competitions.models import Venue
from django.db.models import Q
from documents.models import CertificateTemplate
from pikepdf import Pdf
from problems.logic.results import get_venue_results
from web.models import ContentBlock


def certificates_for_venue(
    venue: Venue, template: CertificateTemplate, empty: bool = False
) -> io.BytesIO:
    buffer = io.BytesIO()

    if not empty:
        results = get_venue_results(venue).prefetch_related("team__contestants")[:3]
    else:
        results = range(3)

    category = (
        ContentBlock.objects.filter(
            group="category",
            branch=venue.category_competition.competition.branch,
            language=venue.accepted_languages[0],  # TODO: Default venue language
            reference=f"name_{venue.category_competition.identifier}",
        )
        .filter(Q(country__isnull=True) | Q(country=venue.country))
        .first()
    )
    if category:
        category = category.content
    else:
        category = "???"

    with Pdf.new() as pdf:
        for rank, row in enumerate(results):
            if empty:
                team = {}
                contestants = range(venue.category_competition.max_members_per_team)
            else:
                team = row.team
                contestants = team.contestants.all()

            context = {
                "team": team,
                "rank": rank + 1,
                "category": category,
                "venue": venue.name,
            }

            if template.for_team:
                data = template.render(context)
                with Pdf.open(io.BytesIO(data)) as cert:
                    pdf.pages.append(cert.pages[0])
            else:
                for contestant in contestants:
                    context["name"] = contestant.full_name if not empty else ""
                    data = template.render(context)
                    with Pdf.open(io.BytesIO(data)) as cert:
                        pdf.pages.append(cert.pages[0])

        pdf.save(buffer)
    buffer.seek(0)
    return buffer
