import io

from competitions.models import Venue
from django.db.models import Q
from documents.models import CertificateTemplate
from pikepdf import Pdf
from problems.logic.results import get_venue_results
from users.models import Team
from web.models import ContentBlock


def certificates_for_venue(venue: Venue, template: CertificateTemplate) -> io.BytesIO:
    buffer = io.BytesIO()
    results = get_venue_results(venue).prefetch_related("team__contestants")[:3]

    with Pdf.new() as pdf:
        for rank, row in enumerate(results):
            team: Team = row.team
            category = (
                ContentBlock.objects.filter(
                    group="category",
                    branch=venue.category_competition.competition.branch,
                    language=team.language,
                    reference=f"name_{venue.category_competition.identifier}",
                )
                .filter(Q(country__isnull=True) | Q(country=venue.country))
                .first()
            )

            if template.for_team:
                context = {
                    "team": team,
                    "rank": rank + 1,
                    "category": category.content if category else "???",
                    "venue": venue.name,
                }
                data = template.render(context)
                with Pdf.open(io.BytesIO(data)) as cert:
                    pdf.pages.append(cert.pages[0])
            else:
                for x, contestant in enumerate(team.contestants.all()):
                    context = {
                        "team": team,
                        "rank": rank + 1,
                        "name": contestant.full_name,
                        "category": category.content if category else "???",
                        "venue": venue.name,
                    }
                    data = template.render(context)
                    with Pdf.open(io.BytesIO(data)) as cert:
                        pdf.pages.append(cert.pages[0])

        pdf.save(buffer)
    buffer.seek(0)
    return buffer
