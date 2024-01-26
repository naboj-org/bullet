from dataclasses import dataclass
from typing import Callable

from django.forms import Form
from django.http import HttpRequest
from django.template.loader import render_to_string


@dataclass
class PageBlock:
    identifier: str
    name: str
    icon: str
    form: Form | None
    context_data: Callable[[HttpRequest, dict], dict] | None

    def render(self, request: HttpRequest, data: dict | None) -> str:
        if data is None:
            data = {}

        ctx = data
        if self.context_data:
            ctx = self.context_data(request, data)

        return render_to_string(f"page_blocks/{self.identifier}.html", ctx, request)
