import io
import zipfile

from competitions.models import Venue
from documents.models import CertificateTemplate
from problems.logic.results import get_venue_results
from users.models import Team
from web.models import ContentBlock


def certificates_for_venue(venue: Venue, template: CertificateTemplate) -> io.BytesIO:
    buffer = io.BytesIO()
    results = get_venue_results(venue).prefetch_related("team__contestants")[:3]

    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rank, row in enumerate(results):
            team: Team = row.team
            category = ContentBlock.objects.filter(
                group="category",
                branch=venue.category_competition.competition.branch,
                country=venue.country,
                language=team.language,
                reference=f"name_{venue.category_competition.identifier}",
            ).first()
            for x, contestant in enumerate(team.contestants.all()):
                context = {
                    "team": team,
                    "rank": rank + 1,
                    "name": contestant.full_name,
                    "category": category.content if category else "???",
                    "venue": venue.name,
                }
                data = template.render(context)
                zf.writestr(f"{rank + 1}_{x + 1}.pdf", data)

    buffer.seek(0)
    return buffer
