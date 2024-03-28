import io
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Table,
    TableStyle,
)


def register_font(name: str):
    font_dir = Path(__file__).parent.parent / "fonts"
    pdfmetrics.registerFont(TTFont(name, font_dir / f"{name}.ttf"))


def prepare_pdf(footer_str: str) -> (io.BytesIO, BaseDocTemplate):
    font_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "fonts")
    pdfmetrics.registerFont(
        TTFont("IBMPlexSans-Regular", os.path.join(font_dir, "IBMPlexSans-Regular.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("IBMPlexSans-Bold", os.path.join(font_dir, "IBMPlexSans-Bold.ttf"))
    )
    pdfmetrics.registerFontFamily(
        "IBMPlexSans", normal="IBMPlexSans-Regular", bold="IBMPlexSans-Bold"
    )

    pdfmetrics.registerFont(
        TTFont("IBMPlexMono-Regular", os.path.join(font_dir, "IBMPlexMono-Regular.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("IBMPlexMono-Bold", os.path.join(font_dir, "IBMPlexMono-Bold.ttf"))
    )
    pdfmetrics.registerFontFamily(
        "IBMPlexMono", normal="IBMPlexMono-Regular", bold="IBMPlexMono-Bold"
    )
    footerStyle = ParagraphStyle(
        name="footer",
        alignment=TA_CENTER,
        fontSize=8,
        leading=10,
        fontName="IBMPlexSans-Bold",
    )

    def footer(canvas, doc):
        canvas.saveState()
        P = Paragraph(
            f"{footer_str}<br/>Page {canvas._pageNumber}",
            footerStyle,
        )
        w, h = P.wrap(doc.width, 0)
        m = 5 * mm
        P.drawOn(canvas, doc.leftMargin, m + 0.5 * mm)
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, m, doc.width + doc.leftMargin, m)
        canvas.line(doc.leftMargin, m + mm + h, doc.width + doc.leftMargin, m + mm + h)
        canvas.restoreState()

    margin = 8 * mm
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=2 * margin,
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        topPadding=0,
    )
    template = PageTemplate(frames=frame, onPage=footer)
    doc.addPageTemplates([template])

    return buffer, doc


def render_table(data, *args, **kwargs) -> Table:
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgray),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), (colors.white, colors.lightgrey)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]
    )
    t = Table(data, *args, **kwargs)
    t.setStyle(style)
    return t
