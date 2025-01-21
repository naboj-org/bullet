import io

from django.db.models import QuerySet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph

from documents.generators.reportlab_utils import prepare_pdf, render_table


def team_list(
    teams: QuerySet, title: str, include_contact=True, include_contestants=True
) -> io.BytesIO:
    teams = (
        teams.order_by("number")
        .prefetch_related("contestants")
        .select_related("school", "venue")
    )

    buf, doc = prepare_pdf(
        "This document contains personal information, "
        "please discard it properly after the competition."
    )

    style_title = ParagraphStyle(
        name="title",
        alignment=TA_CENTER,
        fontSize=18,
        leading=18 * 1.2,
        spaceAfter=4 * mm,
        fontName="IBMPlexSans-Bold",
    )
    style_base = ParagraphStyle(
        name="base", fontSize=10, leading=12, fontName="IBMPlexSans-Regular"
    )
    style_small = ParagraphStyle(
        name="small", fontSize=8, leading=8 * 1.2, fontName="IBMPlexSans-Regular"
    )
    style_bold = ParagraphStyle(
        name="bold", fontSize=10, leading=12, fontName="IBMPlexSans-Bold"
    )
    style_code = ParagraphStyle(
        name="code", fontSize=12, leading=12 * 1.2, fontName="IBMPlexMono-Regular"
    )
    style_code_small = ParagraphStyle(
        name="code-small", fontSize=8, leading=8 * 1.2, fontName="IBMPlexMono-Regular"
    )

    data = []
    header = [
        Paragraph("Number", style_bold),
        Paragraph("School", style_bold),
    ]
    if include_contact:
        header.append(Paragraph("Contact information", style_bold))
    if include_contestants:
        header.append(Paragraph("Contestants", style_bold))
    data.append(header)

    for team in teams:
        contact = []
        if team.contact_email:
            contact.append(team.contact_email)
        if team.contact_phone:
            contact.append(team.contact_phone_pretty)

        row: list = [
            [
                Paragraph(
                    f"{team.venue.shortcode}<b>{team.number:03d}</b>", style_code
                ),
                Paragraph(team.id_display, style_code_small),
            ],
            [
                Paragraph(
                    f"{team.school.name}<b> {team.in_school_symbol or ''}</b>",
                    style_base,
                ),
                Paragraph(team.school.address, style_small),
            ],
        ]

        if include_contact:
            row.append(
                [
                    Paragraph(team.contact_name, style_base),
                    Paragraph("<br/>".join(contact), style_small),
                ]
            )

        if include_contestants:
            row.append(
                Paragraph(
                    "<br/>".join([c.full_name for c in team.contestants.all()]),
                    style_small,
                )
            )

        data.append(row)

    story = []
    story.append(Paragraph(title, style_title))
    story.append(
        render_table(data, colWidths=[25 * mm, None, 50 * mm, 40 * mm], repeatRows=1)
    )
    doc.build(story)
    buf.seek(0)
    return buf
