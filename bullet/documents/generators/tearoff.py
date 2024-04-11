import io
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Sequence

from pikepdf import Page, Pdf, Rectangle
from problems.logic.scanner import get_check_digit
from reportlab.graphics.barcode import code128, qr
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from users.models import Team

from documents.generators.reportlab_utils import register_font


@dataclass
class Tearoff:
    team: Team
    problem_number: int
    page_number: int


class TearoffGenerator:
    stamp_width = 25

    def __init__(self, problem_pdf: Path | BinaryIO):
        self.problem_pdf = Pdf.open(problem_pdf)
        statement_height = float(self.problem_pdf.pages[0].trimbox[3])
        statement_height *= 0.35  # convert pt to mm

        self.statements_per_page = round(297 / statement_height)
        self.statement_height = 297 / self.statements_per_page

        register_font("IBMPlexMono-Regular")
        register_font("IBMPlexMono-Bold")
        register_font("LinLibertine-Regular")
        register_font("LinLibertine-Bold")

    def sequential_tearoffs(
        self, teams: Sequence[Team], problem_count: int, offset: int
    ):
        out = []
        for team in teams:
            for i in range(problem_count):
                page = i + offset
                problem = page + 1
                if i == problem_count - 1:
                    problem = 0
                out.append(Tearoff(team, problem, page))
        return out

    def aligned_tearoffs(self, teams: Sequence[Team], problem_count: int, offset: int):
        out = []
        for team_chunk in chunk_list(teams, self.statements_per_page):
            for i in range(problem_count):
                page = i + offset
                problem = page + 1
                if i == problem_count - 1:
                    problem = 0

                for team in team_chunk:
                    out.append(Tearoff(team, problem, page))

                empty_spaces = self.statements_per_page - len(team_chunk)
                for o in range(empty_spaces):
                    out.append(None)
        return out

    def generate_pdf(
        self, teams: Sequence[Team], first_problem: int, ordering: str
    ) -> BinaryIO:
        offset = first_problem - 1
        problem_count = len(self.problem_pdf.pages) - offset

        tearoffs = []
        if ordering == "seq":
            tearoffs = self.sequential_tearoffs(teams, problem_count, offset)
        if ordering == "align":
            tearoffs = self.aligned_tearoffs(teams, problem_count, offset)

        return self.generate_tearoffs(tearoffs)

    def generate_tearoffs(self, tearoffs: Sequence[Tearoff | None]) -> BinaryIO:
        output_stream = io.BytesIO()
        canvas = Canvas(output_stream)
        pages = chunk_list(tearoffs, self.statements_per_page)

        for page in pages:
            self.add_stamp_page(canvas, page)
            canvas.showPage()
        canvas.save()
        output_stream.seek(0)

        pdf = Pdf.open(output_stream)
        for i, page in enumerate(pages):
            self.add_statements_to_page(pdf.pages[i], page)

        final_stream = io.BytesIO()
        pdf.save(final_stream)
        final_stream.seek(0)
        return final_stream

    def add_stamp_page(self, canvas: Canvas, tearoffs: Iterable[Tearoff | None]):
        for i, tearoff in enumerate(tearoffs):
            if tearoff is None:
                continue
            self._place_stamp(canvas, i * self.statement_height, tearoff)

    def _place_stamp(self, canvas: Canvas, offset_y: float, tearoff: Tearoff):
        canvas.saveState()
        canvas.rotate(90)

        barcode_string = f"{tearoff.team.code}{tearoff.problem_number:02d}"
        barcode_string += str(get_check_digit(barcode_string))

        bar_h = 8
        start_x = (offset_y + 5) * mm
        start_y = (-210 + self.stamp_width - 2) * mm
        max_width = min((self.statement_height - 10) * mm, 100 * mm)
        max_height = (self.stamp_width - 2 - 5) * mm

        canvas.setFillGray(0)
        code = code128.Code128(
            barcode_string, barHeight=bar_h * mm, barWidth=1, quiet=0
        )
        code.barWidth = (max_width - max_height - 2 * mm) / code.width
        code.drawOn(canvas, start_x, start_y - max_height)

        prefix_len = len(tearoff.team.venue.shortcode)
        middle_len = 3
        inverted = False
        if prefix_len == 5:
            prefix_len -= 1
            middle_len += 1
            inverted = tearoff.team.venue.shortcode[-1] == "S"

        font_size = max_height - (bar_h + 0.5) * mm
        canvas.setFillGray(0)
        if inverted:
            canvas.rect(
                start_x,
                start_y,
                max_width - max_height - 2 * mm,
                -font_size,
                fill=True,
                stroke=False,
            )
            canvas.setFillGray(1)

        text = canvas.beginText()
        text.setTextOrigin(start_x, start_y - (bar_h + 0.5) * mm)
        text.setFont("IBMPlexMono-Regular", font_size * 0.5)
        text.textOut(barcode_string[:prefix_len])
        text.setFont("IBMPlexMono-Bold", font_size)
        text.textOut(barcode_string[prefix_len : prefix_len + middle_len])
        text.setFont("IBMPlexMono-Regular", font_size * 0.5)
        text.textOut(barcode_string[prefix_len + middle_len :])
        canvas.drawText(text)

        canvas.setFillGray(0)
        code = qr.QrCode(
            barcode_string, width=max_height, height=max_height, qrBorder=0
        )
        code.drawOn(
            canvas,
            start_x + max_width - max_height,
            start_y - max_height,
        )

        canvas.restoreState()

        text = canvas.beginText()
        text.setTextOrigin(10 * mm, (offset_y + 5) * mm)
        text.setFont("LinLibertine-Bold", 10)
        text.textOut(f"{tearoff.team.code}: ")
        text.setFont("LinLibertine-Regular", 10)
        text.textOut(tearoff.team.display_name_short)
        canvas.drawText(text)

    def add_statements_to_page(self, page: Page, tearoffs: Iterable[Tearoff | None]):
        for i, tearoff in enumerate(tearoffs):
            if tearoff is None:
                continue
            page.add_underlay(
                self.problem_pdf.pages[tearoff.page_number],
                Rectangle(
                    0,
                    self.statement_height * i * mm,
                    210 * mm,
                    self.statement_height * (i + 1) * mm,
                ),
            )


def chunk_list(a, x):
    return [a[i : i + x] for i in range(0, len(a), x)]
