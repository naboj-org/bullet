from django_web_components import component


@component.register("aheader")
class AdminHeader(component.Component):
    template_name = "bullet_admin/components/header.html"


@component.register("asubheader")
class AdminSubheader(component.Component):
    template_name = "bullet_admin/components/subheader.html"


@component.register("abtn")
class AdminButton(component.Component):
    template_name = "bullet_admin/components/button.html"


@component.register("anav")
class AdminNavigation(component.Component):
    template_name = "bullet_admin/components/navigation.html"


@component.register("anavitem")
class AdminNavigationItem(component.Component):
    template_name = "bullet_admin/components/navigation_item.html"


@component.register("abreadcrumbs")
class AdminBreadcrumbs(component.Component):
    template_name = "bullet_admin/components/breadcrumbs.html"


@component.register("abreadcrumb")
class AdminBreadcrumbsItem(component.Component):
    template_name = "bullet_admin/components/breadcrumb.html"
