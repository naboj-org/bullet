from django.conf.global_settings import gettext_noop
from django.db import models


class Languages(models.TextChoices):
    SLOVAK = "sk", gettext_noop("Slovak")
    CZECH = "cs", gettext_noop("Czech")
    ENGLISH = "en", gettext_noop("English")
    GERMAN = "de", gettext_noop("German")
    FINNISH = "fi", gettext_noop("Finnish")
    POLISH = "pl", gettext_noop("Polish")
    MAGYAR = "hu", gettext_noop("Hungarian")
    ROMANIAN = "ro", gettext_noop("Romanian")
    RUSSIAN = "ru", gettext_noop("Russian")
    UKRAINIAN = "uk", gettext_noop("Ukrainian")
    BELARUSSIAN = "be", gettext_noop("Belarusian")
    PERSIAN = "fa", gettext_noop("Persian")
