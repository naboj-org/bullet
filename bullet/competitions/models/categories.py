from competitions.branches import Branches
from django.db import models
from django.db.models import UniqueConstraint
from web.fields import BranchField


class Category(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({Branches[self.branch]})"

    class Meta:
        constraints = [
            UniqueConstraint("branch", "slug", name="category__branch_slug"),
        ]
