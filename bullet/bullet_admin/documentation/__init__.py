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


@dataclass
class Section:
    title: str
    pages: list[Page]


# Sections and their pages appear in the order defined here.
sections = [
    Section(
        "Competition setup",
        [
            Page(
                "competition-init",
                "Creating new competition",
                "Learn about creating and configuring a competition.",
                Access.BRANCH,
            ),
            Page(
                "venues",
                "Creating new venue",
                "Learn about creating and configuring a venue.",
                Access.COUNTRY | Access.BRANCH,
            ),
            Page(
                "permissions",
                "Permissions",
                "Get a better understanding of all the user permissions and "
                "roles in the system.",
                Access.VENUE | Access.COUNTRY | Access.BRANCH,
            ),
        ],
    ),
    Section(
        "Website content",
        [
            Page(
                "pages",
                "Pages and page blocks",
                "Learn how to manage website pages, layouts and "
                "competition-phase visibility.",
                Access.COUNTRY | Access.BRANCH,
            ),
            Page(
                "menu-items",
                "Menu items",
                "Learn how to configure navigation links for each country and language.",
                Access.COUNTRY | Access.BRANCH,
            ),
            Page(
                "file-browser",
                "File browser",
                "Learn how to upload, organise and use public website files.",
                Access.COUNTRY | Access.BRANCH,
            ),
        ],
    ),
    Section(
        "Running the competition",
        [
            Page(
                "teams",
                "Teams",
                'Learn more about viewing and managing teams using the "Teams" page.',
                Access.OPERATOR | Access.VENUE | Access.COUNTRY | Access.BRANCH,
            ),
            Page(
                "problem_scanning",
                "Problem scanning",
                "Learn how to scan solved problems and resolve any problems "
                "that can occur.",
                Access.OPERATOR | Access.VENUE | Access.COUNTRY | Access.BRANCH,
            ),
            Page(
                "results",
                "Results",
                "Learn how to view (unfrozen) results, announce them and "
                "understand how are the teams ordered in the results.",
                Access.OPERATOR | Access.VENUE | Access.COUNTRY | Access.BRANCH,
            ),
            Page(
                "tex",
                "TeX Document Generation",
                "Learn how to generate certificates and other TeX-based documents.",
                Access.VENUE | Access.COUNTRY | Access.BRANCH,
            ),
        ],
    ),
]


def get_page(slug: str):
    for page in get_pages():
        if page.slug == slug:
            return page
    return None


def get_pages():
    return [page for section in sections for page in section.pages]


def get_sections(access: Access) -> list[Section]:
    visible_sections = []
    for section in sections:
        pages = [page for page in section.pages if page.access & access]
        if pages:
            visible_sections.append(Section(section.title, pages))
    return visible_sections
