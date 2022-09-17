from django import template

register = template.Library()


@register.inclusion_tag("form/field.html")
def bfield(field):
    return {"field": field}


@register.inclusion_tag("form/checkbox.html")
def bcheckbox(checkbox):
    return {"checkbox": checkbox}


@register.inclusion_tag("form/form.html")
def bform(form):
    return {"form": form}


@register.inclusion_tag("form/form_vertical.html")
def bformv(form):
    return {"form": form}
