import io
import typing
import zipfile
from os import PathLike

import requests
from django.conf import settings
from jinja2.sandbox import SandboxedEnvironment


def render_zip(
    template_zip: str | PathLike[str] | typing.IO,
    output_zip: str | PathLike[str] | typing.IO,
    context: dict,
):
    env = SandboxedEnvironment(
        block_start_string="(@",
        block_end_string="@)",
        variable_start_string="(*",
        variable_end_string="*)",
        comment_start_string="(%",
        comment_end_string="%)",
        trim_blocks=True,
        autoescape=False,
    )

    with (
        zipfile.ZipFile(template_zip) as template,
        zipfile.ZipFile(output_zip, "w") as output,
    ):
        for file in template.namelist():
            with template.open(file) as f:
                if not file.endswith(".j2"):
                    output.writestr(file, f.read())
                    continue

                j2_template = f.read().decode()
                rendered = env.from_string(j2_template).render(**context)
                target_filename = file.removesuffix(".j2")
                output.writestr(target_filename, rendered)


def send_to_letter(
    template_zip: str | PathLike[str] | typing.IO,
    entrypoint: str,
    context: dict,
    callback: str,
):
    output_zip = io.BytesIO()
    try:
        render_zip(template_zip, output_zip, context)
    finally:
        if hasattr(template_zip, "close"):
            template_zip.close()
    output_zip.seek(0)

    try:
        resp = requests.post(
            f"{settings.LETTER_URL}/async",
            data={
                "entrypoint": entrypoint,
                "callback": settings.LETTER_CALLBACK_ROOT + callback,
            },
            files={"file": output_zip},
            headers={"X-Token": settings.LETTER_TOKEN},
        )
        resp.raise_for_status()
    finally:
        output_zip.close()
