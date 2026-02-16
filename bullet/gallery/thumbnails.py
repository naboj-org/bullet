from pathlib import Path

from django.conf import settings
from django_rq import job
from PIL import Image, ImageFile

from gallery.constants import ORIGNAL_SIZE, THUMB_SIZES
from gallery.models import Photo

ImageFile.LOAD_TRUNCATED_IMAGES = True


def resize_keep_aspect(img: Image.Image, width: int) -> Image.Image:
    height = round(width / img.size[0] * img.size[1])
    return img.resize((width, height), Image.Resampling.BICUBIC)


def make_thumbnails_and_resize(file: str | Path) -> Path:
    img = Image.open(file)
    path = Path(file)
    basename = path.with_suffix("").name

    for size in THUMB_SIZES:
        new_name = path.with_name(f"{basename}_{size}.webp")
        resize_keep_aspect(img, size).save(new_name)

    new_name = path.with_name(f"{basename}.webp")
    resize_keep_aspect(img, ORIGNAL_SIZE).save(new_name)
    return new_name


@job
def resize_photo(photo: Photo | int):
    if isinstance(photo, int):
        photo = Photo.objects.get(id=photo)

    old_image_path = Path(settings.MEDIA_ROOT) / photo.image.name
    new_name = make_thumbnails_and_resize(old_image_path)
    photo.image.name = str(new_name.relative_to(settings.MEDIA_ROOT))
    photo.save()


def delete_thumbnails(file: Path):
    if file.suffix != ".webp":
        return

    basename = file.with_suffix("").name

    for size in THUMB_SIZES:
        thumbnail_file = file.with_name(f"{basename}_{size}.webp")
        if thumbnail_file.exists():
            thumbnail_file.unlink()
