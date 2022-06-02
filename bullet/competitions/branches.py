import dataclasses

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy


@dataclasses.dataclass
class Branch:
    id: int
    identifier: str
    name: str
    short_name: str

    def __int__(self):
        return self.id

    def __str__(self):
        return self.name

    @property
    def domain(self):
        return f"{self.identifier}.{settings.PARENT_HOST}"


class BranchRepository:
    def __init__(self, *branches: Branch):
        self.branches = branches

    def get_from_domain(self, domain: str) -> Branch | None:
        domain = domain.strip().lstrip("www.").lower()
        if not domain.endswith(settings.PARENT_HOST):
            return None

        domain = domain.rstrip(settings.PARENT_HOST).strip(".")
        for b in self.branches:
            if b.identifier == domain:
                return b

    def choices(self) -> list[tuple[int, str]]:
        choices = []
        for b in self.branches:
            choices.append((b.id, b.name))
        return choices

    def __getitem__(self, item):
        if isinstance(item, int):
            for b in self.branches:
                if b.id == item:
                    return b

        if isinstance(item, str):
            for b in self.branches:
                if b.identifier == item:
                    return b

        raise TypeError()

    def __iter__(self):
        return (b for b in self.branches)


Branches = BranchRepository(
    Branch(1, "math", _("Math Náboj"), pgettext_lazy("branch name", "Math")),
    Branch(2, "physics", _("Physics Náboj"), pgettext_lazy("branch name", "Physics")),
    Branch(3, "junior", _("Náboj Junior"), pgettext_lazy("branch name", "Junior")),
)
