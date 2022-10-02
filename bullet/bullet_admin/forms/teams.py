from django import forms
from users.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "school",
            "venue",
            "is_checked_in",
        ]
