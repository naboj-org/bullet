from bullet_admin.fields import FileBrowserInput
from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe

from web.widgets import MarkdownWidget

BackgroundField = forms.ChoiceField(
    label="Background", choices=[("white", "White"), ("color", "Branch color")]
)

PaddingField = forms.ChoiceField(
    label="Spacing", choices=[("normal", "Normal"), ("half", "Half")]
)


class TitleTextMixin(forms.Form):
    title = forms.CharField(label="Title", required=False)
    text = forms.CharField(
        label="Text", required=False, widget=forms.Textarea(attrs={"rows": 3})
    )


class BackgroundMixin(forms.Form):
    background = BackgroundField
    padding = PaddingField


class CompetitionTimelineForm(BackgroundMixin, TitleTextMixin, forms.Form):
    pass


class HeroForm(TitleTextMixin, forms.Form):
    image = forms.CharField(label="Image", required=False, widget=FileBrowserInput())
    cta_text = forms.CharField(label="Button label", required=False)
    cta_url = forms.CharField(label="Button link URL", required=False)


class ImageGridForm(BackgroundMixin, TitleTextMixin, forms.Form):
    pass


class ImageGridItemForm(TitleTextMixin, forms.Form):
    image = forms.CharField(label="Image", required=False, widget=FileBrowserInput())


ImageGridFormset = formset_factory(ImageGridItemForm, extra=4, can_delete=True)


class MarkdownForm(BackgroundMixin, TitleTextMixin, forms.Form):
    content = forms.CharField(
        label="Content",
        help_text="Supports Markdown syntax.",
        required=False,
        widget=MarkdownWidget(attrs={"rows": 20}),
    )

    field_order = ["title", "text", "content", "background"]


class ImageTextForm(BackgroundMixin, TitleTextMixin, forms.Form):
    image = forms.CharField(label="Image", required=False, widget=FileBrowserInput())
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
            "You can find available icons on <a href='https://icones.js.org/collection"
            "/all' target='_blank' class='link'>Icônes</a>."
        ),
    )


IconGridFormset = formset_factory(
    IconGridItemForm, extra=4, can_delete=True, can_order=True
)


class LogoCloudForm(BackgroundMixin, TitleTextMixin, forms.Form):
    align = forms.ChoiceField(
        label="Align",
        choices=[
            ("left", "Left"),
            ("center", "Center"),
            ("spaced", "Spaced"),
            ("right", "Right"),
        ],
    )
    size = forms.FloatField(
        label="Logo size",
        help_text="The height of the logos.",
        required=False,
    )


class LogoCloudItemForm(forms.Form):
    name = forms.CharField(label="Name")
    image = forms.CharField(label="Image", widget=FileBrowserInput())
    url = forms.CharField(label="Link URL")


LogoCloudFormset = formset_factory(
    LogoCloudItemForm, extra=4, can_delete=True, can_order=True
)
