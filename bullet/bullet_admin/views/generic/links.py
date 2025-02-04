from dataclasses import dataclass


@dataclass
class Link:
    color: str
    icon: str | None
    label: str
    url: str


class NewLink(Link):
    def __init__(self, object_name, url):
        super().__init__("green", "mdi:plus", f"New {object_name}", url)


class Icon(Link):
    color = "blue"
    icon = ""
    label = ""

    def __init__(self, url):
        super().__init__(self.color, self.icon, self.label, url)


class HelpLink(Icon):
    icon = "mdi:help"
    label = "Help"
    color = ""


class ViewIcon(Icon):
    icon = "mdi:eye"
    label = "View"


class ExternalViewIcon(Icon):
    icon = "mdi:launch"
    label = "View"


class EditIcon(Icon):
    icon = "mdi:pencil"
    label = "Edit"


class DeleteIcon(Icon):
    icon = "mdi:trash"
    label = "Delete"
    color = "red"
