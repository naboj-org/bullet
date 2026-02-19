from django import forms


class MarkdownWidget(forms.Textarea):
    """A textarea widget that enables Markdown editing."""

    def __init__(self, attrs=None):
        """Initialize the widget with markdown-specific attributes."""
        default_attrs = {
            "data-markdown": "true",
            "class": "markdown-editor",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
