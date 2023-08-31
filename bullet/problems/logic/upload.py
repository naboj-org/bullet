from typing import IO, TYPE_CHECKING
from zipfile import Path, ZipFile

from problems.models import Problem, ProblemStatement

if TYPE_CHECKING:
    from competitions.models import Competition


class ProblemImportError(Exception):
    pass


def handle_upload(competition: "Competition", file: IO[bytes]):
    with ZipFile(file) as zip:
        _handle_statements(competition, zip)


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


def _import_problem(competition: "Competition", language: str, problem_dir: Path):
    """
    Imports a single problem from a directory.

    Expected directory:
    - statement.html
    - answer.html
    - solution.html
    """
    problem = Problem.objects.filter(
        competition=competition, name=problem_dir.name
    ).first()
    if not problem:
        raise ProblemImportError(f"Could not find related problem for {problem_dir}.")

    problem_statement, _ = ProblemStatement.objects.get_or_create(
        problem=problem, language=language.lower()
    )

    statement = problem_dir / "statement.html"
    if statement.exists():
        problem_statement.statement = statement.read_text()

    answer = problem_dir / "answer.html"
    if answer.exists():
        problem_statement.answer = answer.read_text()

    solution = problem_dir / "solution.html"
    if solution.exists():
        problem_statement.solution = solution.read_text()

    problem_statement.save()
