from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from web.models import ContentBlock


def load_blocks(request, *groups):
    if not hasattr(request, "__blocks"):
        request.__blocks = {}
        request.__blocks_loaded = set()

    groups = set(groups)
    groups.difference_update(request.__blocks_loaded)

    if not len(groups):
        return

    blocks = ContentBlock.objects.filter(
        (Q(branch__isnull=True) | Q(branch=request.BRANCH.id))
        & (Q(country__isnull=True) | Q(country=request.COUNTRY_CODE.upper()))
        & Q(language=request.LANGUAGE_CODE)
        & Q(group__in=groups)
    )

    request.__blocks.update(
        {
            (
                b.group,
                b.branch,
                b.country.code.lower() if b.country else None,
                b.reference,
            ): b.content
            for b in blocks
        }
    )
    request.__blocks_loaded.update(groups)


def _render_block(request, group, ref, content, logged_content=None):
    if "showblocks" in request.GET and request.user.is_authenticated:
        link = reverse(
            "badmin:contentblock_trans",
            kwargs={"group": group, "reference": ref},
        )
        if logged_content:
            content = logged_content
        return mark_safe(
            f"<a href='{link}' class='cb-edit' title='{group}:{ref}'>{content}</a>"
        )
    return mark_safe(content)


def get_block(request, combined_ref, allow_empty=False):
    group, ref = combined_ref.split(":", 1)

    if not hasattr(request, "__blocks"):
        raise KeyError("No content blocks were loaded.")
    if group not in request.__blocks_loaded:
        raise KeyError(f"Content block group '{group}' is not loaded.")

    keys = [
        (group, request.BRANCH.id, request.COUNTRY_CODE, ref),
        (group, request.BRANCH.id, None, ref),
        (group, None, request.COUNTRY_CODE, ref),
        (group, None, None, ref),
    ]

    for key in keys:
        if key in request.__blocks:
            return _render_block(request, group, ref, request.__blocks[key])

    if allow_empty:
        return _render_block(request, group, ref, "", f"({group}:{ref})")
    return _render_block(
        request,
        group,
        ref,
        f"<span class='cb-missing'>Missing '{group}:{ref}'</span>",
        f"Missing {group}:{ref}",
    )
