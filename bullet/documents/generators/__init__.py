import os

from django.conf import settings


def prepare_rsvg():
    fonts = settings.MEDIA_ROOT / "fonts"
    os.makedirs(fonts, exist_ok=True)

    # create minimal fontconfig to allow using fonts
    # from custom directory
    conf = fonts / "fonts.conf"
    if not os.path.exists(conf):
        with open(conf, "w") as f:
            f.write(
                f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM '
                f'"urn:fontconfig:fonts.dtd"><fontconfig><dir>{fonts}</dir>'
                f"</fontconfig>"
            )

    return {"FONTCONFIG_PATH": fonts}
