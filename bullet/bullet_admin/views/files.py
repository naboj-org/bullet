from pathlib import Path

from django.conf import settings
from django.views.generic import TemplateView

from bullet_admin.mixins import TranslatorRequiredMixin


class FileTreeView(TranslatorRequiredMixin, TemplateView):
    template_name = "bullet_admin/files/tree.html"

    def get_parents(self):
        path = self.request.GET.get("path", "")
        path = Path(path)
        parents = path.parents
        parents = filter(lambda p: p.name != "", parents)
        parents = map(lambda p: (p.name, str(p)), parents)
        return list(parents)[::-1]

    def get_files(self):
        root: Path = settings.MEDIA_ROOT
        branch_root = root / "files" / self.request.BRANCH.identifier
        path = self.request.GET.get("path", "")
        abs_path = (branch_root / path).resolve()
        if not abs_path.is_relative_to(branch_root):
            return []

        if not abs_path.exists():
            return []

        files = list(abs_path.iterdir())
        files.sort(key=lambda f: f.name)
        files.sort(key=lambda f: not f.is_dir())

        files = [
            {
                "name": f.name,
                "path": f.relative_to(branch_root),
                "is_dir": f.is_dir(),
                "size": f.stat().st_size,
                "public_path": settings.MEDIA_URL + str(f.relative_to(root)),
            }
            for f in files
        ]

        return files

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["files"] = self.get_files()
        ctx["parents"] = self.get_parents()
        return ctx
