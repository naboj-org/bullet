from django import template

register = template.Library()


@register.inclusion_tag("form/field.html")
def bfield(field):
    return {"field": field}


@register.inclusion_tag("form/form.html")
def bform(form):
    return {"form": form}
