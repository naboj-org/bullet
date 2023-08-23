from django_web_components import component


@component.register("aheader")
class AdminHeader(component.Component):
    template_name = "bullet_admin/components/header.html"


@component.register("abtn")
class AdminButton(component.Component):
    template_name = "bullet_admin/components/button.html"
