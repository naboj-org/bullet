from typing import IO, TYPE_CHECKING
from zipfile import Path, ZipFile

from bs4 import BeautifulSoup
from django.core.files.storage import default_storage

from problems.models import Problem, ProblemStatement

if TYPE_CHECKING:
    from competitions.models import Competition


class ProblemImportError(Exception):
    pass


def handle_upload(competition: "Competition", file: IO[bytes]):
    with ZipFile(file) as zip:
        _handle_statements(competition, zip)
        _handle_assets(competition, Path(zip) / "assets")


def _handle_statements(competition: "Competition", zip: ZipFile):
    """
    Imports statements from the zip file.

    Expected folder structure:
    - statements
        - <language> (sk, cs...)
            - <problem_id>
                - statement.html
                - solution.html
                - answer.html
    """
    statement_dir = Path(zip) / "statements"
    if not statement_dir.exists():
        return

    for lang in statement_dir.iterdir():
        if not lang.is_dir():
            continue

        for problem in lang.iterdir():
            if not problem.is_dir():
                continue

            _import_problem(competition, lang.name, problem)


def _replace_links(competition: "Competition", source: str) -> str:
    """
    Replaces <img src="..."> with proper paths.
    """
    soup = BeautifulSoup(source, "html.parser")
    for img_tag in soup.find_all("img"):
        src: str = img_tag["src"]
        if src.startswith("http://") or src.startswith("https://"):
            continue
        img_tag["src"] = default_storage.url(competition.secret_dir / "assets" / src)
    return str(soup)


def _import_problem(competition: "Competition", language: str, problem_dir: Path):
    """
    Imports a single problem from a directory.

    Expected directory:
    - statement.html
    - answer.html
    - solution.html
    """
    problem = Problem.objects.filter(
        competition=competition, number=problem_dir.name
    ).first()
    if not problem:
        raise ProblemImportError(f"Could not find related problem for {problem_dir}.")

    problem_statement, _ = ProblemStatement.objects.get_or_create(
        problem=problem, language=language.lower()
    )

    statement = problem_dir / "statement.html"
    if statement.exists():
        problem_statement.statement = _replace_links(competition, statement.read_text())

    answer = problem_dir / "answer.html"
    if answer.exists():
        problem_statement.answer = _replace_links(competition, answer.read_text())

    solution = problem_dir / "solution.html"
    if solution.exists():
        problem_statement.solution = _replace_links(competition, solution.read_text())

    problem_statement.save()


def _handle_assets(competition: "Competition", path: Path):
    """
    Uploads all assets to the server.
    """
    if not path.exists():
        return

    for file in path.iterdir():
        if file.is_dir():
            _handle_assets(competition, file)
        else:
            _, file_normalized = str(file).split("/assets/", 1)
            with file.open("rb") as f:
                upload_path = competition.secret_dir / "assets" / file_normalized
                default_storage.delete(upload_path)
                default_storage.save(upload_path, f)
