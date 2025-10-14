import io
from dataclasses import dataclass
from operator import attrgetter
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


class TearoffRequirementMissingError(Exception):
    pass


class TearoffGenerator:
    stamp_width = 25

    def __init__(self, problem_pdf_root: Path, primary_language: str):
        self._problem_pdfs = {}
        self.problem_pdf_root = problem_pdf_root
        statement_height = float(
            self.get_problem_pdf(primary_language).pages[0].trimbox[3]
        )
        statement_height *= 0.35  # convert pt to mm

        self.statements_per_page = round(297 / statement_height)
        self.statement_height = 297 / self.statements_per_page

        register_font("IBMPlexMono-Regular")
        register_font("IBMPlexMono-Bold")
        register_font("LinLibertine-Regular")
        register_font("LinLibertine-Bold")

    def get_problem_pdf(self, language: str):
        if language not in self._problem_pdfs:
            try:
                self._problem_pdfs[language] = Pdf.open(
                    self.problem_pdf_root / f"{language}.pdf"
                )
            except FileNotFoundError:
                raise TearoffRequirementMissingError(
                    f"Missing tearoff file for language {language}."
                )
        return self._problem_pdfs[language]

    def close_problem_pdfs(self):
        for pdf in self._problem_pdfs.values():
            pdf.close()

    def check_requirements(self, teams: Sequence[Team], problem_count: int):
        languages = set(map(attrgetter("language"), teams))
        for language in languages:
            try:
                problem_pdf = self.get_problem_pdf(language)
            except TearoffRequirementMissingError:
                raise

            if len(problem_pdf.pages) != problem_count + 1:
                raise TearoffRequirementMissingError(
                    f"Wrong page count for language {language}: expected "
                    f"{problem_count + 1}, got {len(problem_pdf.pages)}."
                )

    def sequential_tearoffs(
        self, teams: Sequence[Team], problem_count: int, offset: int
    ):
        out = []
        for team in teams:
            for i in range(problem_count + 1):
                page = i + offset
                problem = page + 1
                if i == problem_count:
                    problem = 0
                out.append(Tearoff(team, problem, page))
        return out

    def aligned_tearoffs(self, teams: Sequence[Team], problem_count: int, offset: int):
        out = []
        for team_chunk in chunk_list(teams, self.statements_per_page):
            for i in range(problem_count + 1):
                page = i + offset
                problem = page + 1
                if i == problem_count:
                    problem = 0

                for team in team_chunk:
                    out.append(Tearoff(team, problem, page))

                empty_spaces = self.statements_per_page - len(team_chunk)
                for o in range(empty_spaces):
                    out.append(None)
        return out

    def generate_pdf(
        self,
        teams: Sequence[Team],
        first_problem: int,
        problem_count: int,
        ordering: str,
        include_qr: bool = True,
    ) -> BinaryIO:
        self.check_requirements(teams, problem_count)

        offset = first_problem - 1
        problem_count -= offset

        tearoffs = []
        if ordering == "seq":
            tearoffs = self.sequential_tearoffs(teams, problem_count, offset)
        if ordering == "align":
            tearoffs = self.aligned_tearoffs(teams, problem_count, offset)

        return self.generate_tearoffs(tearoffs, include_qr)

    def generate_tearoffs(
        self, tearoffs: Sequence[Tearoff | None], include_qr: bool
    ) -> BinaryIO:
        output_stream = io.BytesIO()
        canvas = Canvas(output_stream)
        pages = chunk_list(tearoffs, self.statements_per_page)

        for page in pages:
            self.add_stamp_page(canvas, page, include_qr)
            canvas.showPage()
        canvas.save()
        output_stream.seek(0)

        pdf = Pdf.open(output_stream)
        for i, page in enumerate(pages):
            self.add_statements_to_page(pdf.pages[i], page)

        final_stream = io.BytesIO()
        pdf.save(final_stream)
        final_stream.seek(0)
        self.close_problem_pdfs()
        return final_stream

    def add_stamp_page(
        self, canvas: Canvas, tearoffs: Iterable[Tearoff | None], include_qr: bool
    ):
        for i, tearoff in enumerate(tearoffs):
            if tearoff is None:
                continue
            self._place_stamp(canvas, i * self.statement_height, tearoff, include_qr)

    def _place_stamp(
        self, canvas: Canvas, offset_y: float, tearoff: Tearoff, include_qr: bool
    ):
        canvas.saveState()
        canvas.rotate(90)

        barcode_string = f"{tearoff.team.code}{tearoff.problem_number:02d}"
        barcode_string += str(get_check_digit(barcode_string))

        bar_h = 8
        start_x = (offset_y + 5) * mm
        start_y = (-210 + self.stamp_width + 2) * mm
        max_width = (self.statement_height - 10) * mm
        max_height = (self.stamp_width - 2 - 5) * mm
        school_length = max_width

        if max_width > 75 * mm:
            start_x += (max_width - 75 * mm) / 2
            max_width = 75 * mm
            school_length = max_width

        if not include_qr:
            start_x += max_height / 2
            school_length -= max_height

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
        spacing = 2 * mm if inverted else 1 * mm

        text = canvas.beginText()
        text.setTextOrigin(start_x, start_y - (bar_h + 0.5) * mm)
        text.setFont("IBMPlexMono-Regular", font_size * 0.45)
        text.textOut(barcode_string[:prefix_len])

        inverted_start = text.getX()
        where_am_i = text.getX() - text.getStartOfLine()[0]
        text.setXPos(where_am_i + spacing)
        if inverted:
            text.setFillGray(1)
        text.setFont("IBMPlexMono-Bold", font_size)
        text.textOut(barcode_string[prefix_len : prefix_len + middle_len])
        where_am_i = text.getX() - text.getStartOfLine()[0]
        text.setXPos(where_am_i + spacing)
        if inverted:
            text.setFillGray(0)
        inverted_end = text.getX()

        text.setFont("IBMPlexMono-Regular", font_size * 0.45)
        text.textOut(barcode_string[prefix_len + middle_len :])

        if inverted:
            canvas.rect(
                inverted_start + 1 * mm,
                start_y,
                inverted_end - inverted_start - 2 * mm,
                -font_size,
                fill=True,
                stroke=False,
            )

        canvas.drawText(text)

        if include_qr:
            canvas.setFillGray(0)
            code = qr.QrCode(
                barcode_string, width=max_height, height=max_height, qrBorder=0
            )
            code.drawOn(
                canvas,
                start_x + max_width - max_height,
                start_y - max_height,
            )

        text = canvas.beginText()
        text.setTextOrigin(start_x, start_y - max_height - 8)
        text.setFont("IBMPlexMono-Regular", 6)
        school_chars = (
            int(school_length / mm * 0.77) - 1
        )  # 0.77 is how many characters fit in a mm of space
        text.textOut(tearoff.team.get_shortened_display_name(school_chars))
        canvas.drawText(text)

        canvas.restoreState()

    def add_statements_to_page(self, page: Page, tearoffs: Iterable[Tearoff | None]):
        for i, tearoff in enumerate(tearoffs):
            if tearoff is None:
                continue
            pdf_file = self.get_problem_pdf(tearoff.team.language)
            page.add_underlay(
                pdf_file.pages[tearoff.page_number],
                Rectangle(
                    0,
                    self.statement_height * i * mm,
                    210 * mm,
                    self.statement_height * (i + 1) * mm,
                ),
            )


def chunk_list(a, x):
    return [a[i : i + x] for i in range(0, len(a), x)]
