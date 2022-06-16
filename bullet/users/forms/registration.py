from competitions.models import Category
from django import forms


class CategorySelectForm(forms.Form):
    category = forms.ChoiceField()

    def __init__(self, categories: list[Category], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [(c.id, str(c)) for c in categories]
