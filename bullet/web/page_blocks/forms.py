from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe

BackgroundField = forms.ChoiceField(
    label="Background", choices=[("white", "White"), ("color", "Branch color")]
)


class TitleTextMixin(forms.Form):
    title = forms.CharField(label="Title", required=False)
    text = forms.CharField(
        label="Text", required=False, widget=forms.Textarea(attrs={"rows": 3})
    )


class BackgroundMixin(forms.Form):
    background = BackgroundField


class CompetitionTimelineForm(TitleTextMixin, forms.Form):
    background = BackgroundField


class HeroForm(TitleTextMixin, forms.Form):
    image = forms.CharField(label="Image", required=False)  # TODO: use new file picker
    cta_text = forms.CharField(label="Button label", required=False)
    cta_url = forms.CharField(label="Button link URL", required=False)


class ImageGridForm(BackgroundMixin, TitleTextMixin, forms.Form):
    pass


class ImageGridItemForm(TitleTextMixin, forms.Form):
    image = forms.CharField(label="Image", required=False)  # TODO: use new file picker


ImageGridFormset = formset_factory(ImageGridItemForm, extra=4, can_delete=True)


class MarkdownForm(BackgroundMixin, TitleTextMixin, forms.Form):
    content = forms.CharField(
        label="Content",
        help_text="Supports Markdown syntax.",
        required=False,
        widget=forms.Textarea(attrs={"rows": 20}),
    )

    field_order = ["title", "text", "content", "background"]


class ImageTextForm(BackgroundMixin, TitleTextMixin, forms.Form):
    image = forms.CharField(label="Image", required=False)  # TODO: use new file picker
    side = forms.ChoiceField(
        label="Image position",
        choices=[("left", "Image on the left"), ("right", "Image on the right")],
    )

    cta_text = forms.CharField(label="Button label", required=False)
    cta_url = forms.CharField(label="Button link URL", required=False)

    field_order = [
        "title",
        "text",
        "image",
        "side",
        "cta_text",
        "cta_url",
        "background",
    ]


class IconGridForm(BackgroundMixin, TitleTextMixin, forms.Form):
    pass


class IconGridItemForm(TitleTextMixin, forms.Form):
    icon = forms.CharField(
        label="Icon",
        help_text=mark_safe(
            "You can find available icons on <a href='https://icones.js.org/collection/all' target='_blank' class='link'>Icônes</a>."
        ),
    )


IconGridFormset = formset_factory(IconGridItemForm, extra=4, can_delete=True)


class LogoCloudForm(BackgroundMixin, TitleTextMixin, forms.Form):
    pass


class LogoCloudItemForm(forms.Form):
    name = forms.CharField(label="Name")
    image = forms.CharField(label="Image")  # TODO: use new file picker
    url = forms.CharField(label="Link URL")
    size = forms.IntegerField(
        label="Size",
        help_text="How many colums of the grid should this logo take.",
        required=False,
    )


LogoCloudFormset = formset_factory(LogoCloudItemForm, extra=4, can_delete=True)
