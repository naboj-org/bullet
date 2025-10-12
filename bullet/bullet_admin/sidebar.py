from dataclasses import dataclass

from competitions.models.competitions import Competition
from django.urls import reverse_lazy
from users.models.organizers import User

from bullet_admin.access_v2 import PermissionCallable, check_access
from bullet_admin.views.album import AlbumListView
from bullet_admin.views.archive import ProblemImportView, ProblemPDFUploadView
from bullet_admin.views.category import CategoryListView
from bullet_admin.views.competition import (
    CompetitionAutomoveView,
    CompetitionTearoffUploadView,
    CompetitionUpdateView,
)
from bullet_admin.views.content import (
    ContentBlockListView,
    MenuItemListView,
    PageListView,
)
from bullet_admin.views.education import SchoolListView
from bullet_admin.views.emails import CampaignListView
from bullet_admin.views.files import FileTreeView
from bullet_admin.views.results import ResultsHomeView
from bullet_admin.views.scanning import ProblemScanView, VenueReviewView
from bullet_admin.views.teams import RecentlyDeletedTeamsView, TeamListView
from bullet_admin.views.tex import TemplateListView
from bullet_admin.views.users import UserListView
from bullet_admin.views.venues import VenueListView
from bullet_admin.views.wildcards import WildcardListView


@dataclass
class Item:
    icon: str
    name: str
    link: str
    permissions: list[PermissionCallable] | PermissionCallable


@dataclass
class Group:
    name: str
    items: list[Item]


SIDEBAR: list[Group] = [
    Group(
        "Competition",
        [
            Item(
                "mdi:account-group",
                "Teams",
                reverse_lazy("badmin:team_list"),
                TeamListView.required_permissions,
            ),
            Item(
                "mdi:email",
                "Email campaigns",
                reverse_lazy("badmin:email_list"),
                CampaignListView.required_permissions,
            ),
            Item(
                "mdi:delete-clock",
                "Deleted teams",
                reverse_lazy("badmin:recently_deleted"),
                RecentlyDeletedTeamsView.required_permissions,
            ),
            Item(
                "mdi:barcode-scan",
                "Problem scanning",
                reverse_lazy("badmin:scanning_problems"),
                ProblemScanView.required_permissions,
            ),
            Item(
                "mdi:magnify",
                "Review",
                reverse_lazy("badmin:scanning_review"),
                VenueReviewView.required_permissions,
            ),
            Item(
                "mdi:trophy",
                "Results",
                reverse_lazy("badmin:results"),
                ResultsHomeView.required_permissions,
            ),
            Item(
                "mdi:star",
                "Wildcards",
                reverse_lazy("badmin:wildcard_list"),
                WildcardListView.required_permissions,
            ),
        ],
    ),
    Group(
        "Content",
        [
            Item(
                "mdi:file-document",
                "Pages",
                reverse_lazy("badmin:page_list"),
                PageListView.required_permissions,
            ),
            Item(
                "mdi:menu",
                "Menu items",
                reverse_lazy("badmin:menu_list"),
                MenuItemListView.required_permissions,
            ),
            Item(
                "mdi:folder-open",
                "File browser",
                reverse_lazy("badmin:file_tree"),
                FileTreeView.required_permissions,
            ),
            Item(
                "mdi:image",
                "Photos",
                reverse_lazy("badmin:album_list"),
                AlbumListView.required_permissions,
            ),
            Item(
                "mdi:cube-outline",
                "Content blocks",
                reverse_lazy("badmin:contentblock_list"),
                ContentBlockListView.required_permissions,
            ),
        ],
    ),
    Group(
        "Settings",
        [
            Item(
                "mdi:account-cowboy-hat",
                "Users",
                reverse_lazy("badmin:user_list"),
                UserListView.required_permissions,
            ),
            Item(
                "mdi:school",
                "Schools",
                reverse_lazy("badmin:school_list"),
                SchoolListView.required_permissions,
            ),
            Item(
                "mdi:map-marker",
                "Venues",
                reverse_lazy("badmin:venue_list"),
                VenueListView.required_permissions,
            ),
            Item(
                "mdi:select-compare",
                "Categories",
                reverse_lazy("badmin:category_list"),
                CategoryListView.required_permissions,
            ),
            Item(
                "mdi:cog",
                "Competition",
                reverse_lazy("badmin:competition_edit"),
                CompetitionUpdateView.required_permissions,
            ),
            Item(
                "mdi:format-paint",
                "TeX templates",
                reverse_lazy("badmin:tex_template_list"),
                TemplateListView.required_permissions,
            ),
            Item(
                "mdi:fast-forward",
                "Move waiting lists",
                reverse_lazy("badmin:competition_automove"),
                CompetitionAutomoveView.required_permissions,
            ),
        ],
    ),
    Group(
        "Problems",
        [
            Item(
                "mdi:format-page-break",
                "Upload tearoffs",
                reverse_lazy("badmin:competition_upload_tearoffs"),
                CompetitionTearoffUploadView.required_permissions,
            ),
            Item(
                "mdi:book-open-blank-variant",
                "Upload booklets",
                reverse_lazy("badmin:archive_problem_upload"),
                ProblemPDFUploadView.required_permissions,
            ),
            Item(
                "mdi:archive",
                "Upload archive data",
                reverse_lazy("badmin:archive_import"),
                ProblemImportView.required_permissions,
            ),
        ],
    ),
]


def get_sidebar(user: User, competition: Competition) -> list[Group]:
    real_sidebar = []

    for group in SIDEBAR:
        items = list(
            filter(
                lambda i: check_access(
                    user,
                    i.permissions
                    if isinstance(i.permissions, list)
                    else [i.permissions],
                    competition=competition,
                ),
                group.items,
            )
        )

        if items:
            real_sidebar.append(Group(group.name, items))

    return real_sidebar
