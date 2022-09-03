from django.db import models
from django_countries.fields import CountryField
from web.fields import BranchField


class BranchRole(models.Model):
    class Role(models.TextChoices):
        BRANCH = "BRANCH", "Branch administrator"
        COUNTRY = "COUNTRY", "Country administrator"
        VENUE = "VENUE", "Venue administrator"
        NONE = "NONE", "No role"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    branch = BranchField()
    role = models.CharField(choices=Role.choices, max_length=10)
    country = CountryField(blank=True, null=True)
    venue = models.ForeignKey(
        "competitions.Venue",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="+",
    )
    can_translate = models.BooleanField(default=False)
    can_delegate = models.BooleanField(default=False)

    class Meta:
        constraints = (
            models.UniqueConstraint("user", "branch", name="branch_role__user_branch"),
        )
