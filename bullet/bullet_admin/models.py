from django.db import models
from django_countries.fields import CountryField
from web.fields import BranchField, ChoiceArrayField


class BranchRole(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    branch = BranchField()
    is_translator = models.BooleanField(default=False)
    is_school_editor = models.BooleanField(default=False)
    is_photographer = models.BooleanField(default=False)
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
    countries = ChoiceArrayField(CountryField(), blank=True, null=True)
    venue_objects = models.ManyToManyField(
        "competitions.Venue",
        related_name="+",
        blank=True,
    )
    can_delegate = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)

    @property
    def venues(self):
        if not self.id:
            return []
        return self.venue_objects.all()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                "user", "competition", name="competition_role__user_competition"
            ),
        )
