import re
from dataclasses import dataclass
from datetime import datetime

from competitions.models import Competition, Venue
from django.db import transaction
from django.utils import timezone
from problems.logic import get_last_problem_for_team, mark_problem_solved
from problems.models import Problem, SolvedProblem
from users.models import Team

barcode_re = re.compile(
    r"^(?P<venue>[A-Z]+)(?P<team>[0-9]+)(?P<problem>[0-9]{2})(?P<checksum>[0-9])$"
)


def get_check_digit(data: str) -> int:
    weights = [7, 3, 1]
    checksum = []

    for i, char in enumerate(data.upper()):
        w = weights[i % 3]
        if char.isalpha():
            checksum.append(w * (10 + ord(char) - ord("A")))
        elif char.isnumeric():
            checksum.append(w * int(char))
        else:
            raise ValueError(f"Found invalid character '{char}' in barcode")

    return sum(checksum) % 10


def verify_check_digit(data: str) -> bool:
    check_digit = get_check_digit(data[:-1])
    return str(check_digit) == data[-1]


@dataclass
class ScannedBarcode:
    venue: Venue
    team: Team
    problem_number: int
    problem: Problem


def parse_barcode(
    competition: Competition, barcode: str, allow_endmark=False
) -> ScannedBarcode:
    match = barcode_re.match(barcode)
    if not match:
        raise ValueError("Barcode format is invalid.")

    if not verify_check_digit(barcode):
        raise ValueError("Check digit on the scanned barcode is not correct.")

    venue = Venue.objects.filter(
        shortcode=match.group("venue"), category_competition__competition=competition
    ).first()
    if not venue:
        raise ValueError(f"Could not find venue {match.group('venue')}.")

    team = Team.objects.filter(number=match.group("team"), venue=venue).first()
    if not team:
        raise ValueError(
            f"Could not find team {match.group('team')} in {venue.shortcode}."
        )

    if allow_endmark and int(match.group("problem")) == 0:
        problem = None
    else:
        problem = Problem.objects.filter(
            competition=competition,
            category_problems__category=venue.category_competition,
            category_problems__number=match.group("problem"),
        ).first()
        if not problem:
            raise ValueError(f"Could not find problem {match.group('problem')}.")

    return ScannedBarcode(venue, team, int(match.group("problem")), problem)


@transaction.atomic
def save_scan(
    scanned_barcode: ScannedBarcode,
    timestamp: datetime = None,
):
    if not timestamp:
        timestamp = timezone.now()

    # Check if team has this problem
    if get_last_problem_for_team(scanned_barcode.team) < scanned_barcode.problem_number:
        raise ValueError(
            f"Team should not have access to problem {scanned_barcode.problem_number}."
        )

    # Check if team solved this problem
    if SolvedProblem.objects.filter(
        team=scanned_barcode.team, problem=scanned_barcode.problem
    ).exists():
        raise ValueError(
            f"Team already solved problem {scanned_barcode.problem_number}."
        )

    # Mark the team as checked in if not already
    if not scanned_barcode.team.is_checked_in:
        scanned_barcode.team.is_checked_in = True
        scanned_barcode.team.save()

    mark_problem_solved(scanned_barcode.team, scanned_barcode.problem, timestamp)
