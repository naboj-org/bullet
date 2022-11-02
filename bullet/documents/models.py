import subprocess

from django.db import models
from django.template import Context, Template
from documents.generators import prepare_rsvg
from web.fields import BranchField


class CertificateTemplate(models.Model):
    name = models.CharField(max_length=128)
    branch = BranchField()
    template = models.TextField()

    def render(self, context: dict, output_format="pdf") -> bytes:
        template = Template(self.template)
        context = Context(context)
        source = template.render(context)
        env = prepare_rsvg()
        data = subprocess.check_output(
            [
                "rsvg-convert",
                "--format",
                output_format,
                "--dpi-x",
                "300",
                "--dpi-y",
                "300",
            ],
            input=source.encode("utf-8"),
            env=env,
        )
        return data

    def __str__(self):
        return self.name
