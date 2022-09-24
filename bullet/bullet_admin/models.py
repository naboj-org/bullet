from django.db import models
from django_countries.fields import CountryField
from web.fields import BranchField


class BranchRole(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    branch = BranchField()
    is_translator = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        constraints = (
            models.UniqueConstraint("user", "branch", name="branch_role__user_branch"),
        )


class CompetitionRole(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE
    )
    country = CountryField(blank=True, null=True)
    venue = models.ForeignKey(
        "competitions.Venue",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="+",
    )
    can_delegate = models.BooleanField(default=False)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                "user", "competition", name="competition_role__user_competition"
            ),
        )
