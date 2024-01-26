from web.page_blocks import PageBlock, competition_timeline

PAGE_BLOCK_TYPES = {
    1: PageBlock("logo_cloud", "Logo cloud", "mdi:view-grid-outline", None, None),
    2: PageBlock("image_text", "Text with image on side", "mdi:image-text", None, None),
    3: PageBlock("icon_grid", "Grid with icons", "mdi:format-list-text", None, None),
    4: PageBlock(
        "competition_timeline",
        "Competition timeline",
        "mdi:timeline-clock-outline",
        None,
        competition_timeline.get_context,
    ),
    5: PageBlock("hero", "Hero header", "mdi:page-layout-header", None, None),
    6: PageBlock("markdown", "Markdown text", "mdi:language-markdown", None, None),
    7: PageBlock("image_grid", "Image grid", "mdi:file-image-box", None, None),
}


def get_page_block_choices():
    return [(k, v.name) for k, v in PAGE_BLOCK_TYPES.items()]
