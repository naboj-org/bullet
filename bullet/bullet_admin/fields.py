from django.forms import TextInput


class FileBrowserInput(TextInput):
    input_type = "file_browser"


class SchoolInput(TextInput):
    input_type = "school_input"
