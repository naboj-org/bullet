from dataclasses import dataclass
from enum import Flag, auto
from pathlib import Path


class Access(Flag):
    OPERATOR = auto()
    VENUE = auto()
    COUNTRY = auto()
    BRANCH = auto()

    def allows_operator(self) -> bool:
        return bool(self & Access.OPERATOR)

    def allows_venue_admin(self) -> bool:
        return bool(self & Access.VENUE)

    def allows_country_admin(self) -> bool:
        return bool(self & Access.COUNTRY)

    def allows_branch_admin(self) -> bool:
        return bool(self & Access.BRANCH)


@dataclass
class Page:
    slug: str
    title: str
    description: str
    access: Access

    @property
    def content(self):
        file = (Path(__file__).parent / self.slug).with_suffix(".md")
        return file.read_text()


pages = [
    Page(
        "teams",
        "Teams",
        'Learn more about viewing and managing teams using the "Teams" page.',
        Access.OPERATOR | Access.VENUE | Access.COUNTRY | Access.BRANCH,
    ),
    Page(
        "permissions",
        "Permissions",
        "Get a better understanding of all the user permissions and roles in the "
        "system.",
        Access.VENUE | Access.COUNTRY | Access.BRANCH,
    ),
    Page(
        "results",
        "Results",
        "Learn how to view (unfrozen) results, announce them and understand how are "
        "the teams ordered in the results.",
        Access.OPERATOR | Access.VENUE | Access.COUNTRY | Access.BRANCH,
    ),
    Page(
        "problem_scanning",
        "Problem scanning",
        "Learn how to scan solved problems and resolve any problems that can occur.",
        Access.OPERATOR | Access.VENUE | Access.COUNTRY | Access.BRANCH,
    ),
]


def get_page(slug: str):
    for p in pages:
        if p.slug == slug:
            return p
    return None


def get_pages():
    return sorted(pages, key=lambda p: p.title)
