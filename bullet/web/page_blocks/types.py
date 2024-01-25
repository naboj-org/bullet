from web.page_blocks import PageBlock, competition_timeline

PAGE_BLOCK_TYPES = {
    1: PageBlock("logo_cloud", "Logo cloud", None, None),
    2: PageBlock("image_text", "Text with image on side", None, None),
    3: PageBlock("icon_grid", "Grid with icons", None, None),
    4: PageBlock(
        "competition_timeline",
        "Competition timeline",
        None,
        competition_timeline.get_context,
    ),
}


def get_page_block_choices():
    return [(k, v.name) for k, v in PAGE_BLOCK_TYPES.items()]
