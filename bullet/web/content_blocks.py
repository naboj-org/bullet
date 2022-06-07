from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from web.models import ContentBlock

_blocks_cache = {}


def get_blocks_cache():
    if len(_blocks_cache) == 0:
        blocks = ContentBlock.objects.all()
        for block in blocks:
            key = (
                block.branch,
                block.country.code.lower() if block.country else None,
                block.language,
                block.reference,
            )
            _blocks_cache[key] = block.content

    return _blocks_cache


@receiver(post_save, sender=ContentBlock)
@receiver(post_delete, sender=ContentBlock)
def reset_cache(**kwargs):
    _blocks_cache.clear()
