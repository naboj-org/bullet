import io

from competitions.models import Venue
from django.db.models import Q
from pikepdf import Pdf
from problems.logic.results import get_venue_results
from users.models import Team
from web.models import ContentBlock

from documents.models import CertificateTemplate


def _get_category_name(venue: Venue) -> str:
    category = (
        ContentBlock.objects.filter(
            group="category",
            branch=venue.category.competition.branch,
            language=venue.accepted_languages[0],  # TODO: Default venue language
            reference=f"name_{venue.category.identifier}",
        )
        .filter(Q(country__isnull=True) | Q(country=venue.country))
        .first()
    )
    if category:
        return category.content
    else:
        return "???"


def _one_certificate(
    template: CertificateTemplate,
    team: Team,
    rank: int,
    category: str,
    venue: Venue,
    contestant: str,
) -> bytes:
    context = {
        "team": team,
        "rank": rank,
        "category": category,
        "venue": venue.name,
        "name": contestant,
    }

    return template.render(context)


def certificates_for_venue(
    venue: Venue, template: CertificateTemplate, count: int = 3, empty: bool = False
) -> io.BytesIO:
    buffer = io.BytesIO()

    if not empty:
        results = get_venue_results(venue).prefetch_related("team__contestants")
        if count:
            results = results[:count]
        else:
            results = results.all()
    else:
        results = range(count)

    category = _get_category_name(venue)

    with Pdf.new() as pdf:
        for rank, row in enumerate(results):
            if empty:
                team = {}
                contestants = range(venue.category.max_members_per_team)
            else:
                team = row.team
                contestants = team.contestants.all()

            if template.for_team:
                data = _one_certificate(template, team, rank + 1, category, venue, "")
                with Pdf.open(io.BytesIO(data)) as cert:
                    pdf.pages.append(cert.pages[0])
            else:
                for contestant in contestants:
                    data = _one_certificate(
                        template,
                        team,
                        rank + 1,
                        category,
                        venue,
                        contestant.full_name if not empty else "",
                    )
                    with Pdf.open(io.BytesIO(data)) as cert:
                        pdf.pages.append(cert.pages[0])

        pdf.save(buffer)
    buffer.seek(0)
    return buffer


def certificate_for_team(template: CertificateTemplate, team: Team) -> io.BytesIO:
    results = get_venue_results(team.venue)
    rank = "???"
    for i, t in enumerate(results):
        if t.team == team:
            rank = i + 1
            break

    category = _get_category_name(team.venue)

    buffer = io.BytesIO()
    with Pdf.new() as pdf:
        if template.for_team:
            data = _one_certificate(template, team, rank, category, team.venue, "")
            with Pdf.open(io.BytesIO(data)) as cert:
                pdf.pages.append(cert.pages[0])
        else:
            for contestant in team.contestants.all():
                data = _one_certificate(
                    template, team, rank, category, team.venue, contestant.full_name
                )
                with Pdf.open(io.BytesIO(data)) as cert:
                    pdf.pages.append(cert.pages[0])
        pdf.save(buffer)
    buffer.seek(0)
    return buffer
