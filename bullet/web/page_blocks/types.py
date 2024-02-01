from web.page_blocks import PageBlock
from web.page_blocks.contexts import competition_timeline_context
from web.page_blocks.forms import (
    CompetitionTimelineForm,
    HeroForm,
    IconGridForm,
    IconGridFormset,
    ImageGridForm,
    ImageGridFormset,
    ImageTextForm,
    LogoCloudForm,
    LogoCloudFormset,
    MarkdownForm,
)

PAGE_BLOCK_TYPES = {
    1: PageBlock(
        "logo_cloud",
        "Logo cloud",
        "mdi:view-grid-outline",
        LogoCloudForm,
        LogoCloudFormset,
    ),
    2: PageBlock(
        "image_text",
        "Text with image on side",
        "mdi:image-text",
        ImageTextForm,
    ),
    3: PageBlock(
        "icon_grid",
        "Grid with icons",
        "mdi:format-list-text",
        IconGridForm,
        IconGridFormset,
    ),
    4: PageBlock(
        "competition_timeline",
        "Competition timeline",
        "mdi:timeline-clock-outline",
        CompetitionTimelineForm,
        context_data=competition_timeline_context,
    ),
    5: PageBlock("hero", "Main header", "mdi:page-layout-header", HeroForm),
    6: PageBlock(
        "markdown",
        "Markdown text",
        "mdi:language-markdown",
        MarkdownForm,
    ),
    7: PageBlock(
        "image_grid",
        "Grid with images",
        "mdi:file-image-box",
        ImageGridForm,
        ImageGridFormset,
    ),
}


def get_page_block_choices():
    return [(k, v.name) for k, v in PAGE_BLOCK_TYPES.items()]
