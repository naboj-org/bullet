from django import template

register = template.Library()


@register.inclusion_tag("bullet_admin/partials/sidebar_menu.html")
def admin_sidebar():
    menu_items = (
        (
            "Competition",
            (
                ("fa-users", "Teams", "#"),
                ("fa-barcode", "Something", "#"),
            ),
        ),
    )

    return {"menu_items": menu_items}
