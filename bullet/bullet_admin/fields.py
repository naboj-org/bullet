from django.forms import TextInput


class FileBrowserInput(TextInput):
    input_type = "file_browser"
