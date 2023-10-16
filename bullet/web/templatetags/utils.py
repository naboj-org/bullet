from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return f"?{query.urlencode()}"


@register.simple_tag
def query_replace(**kwargs):
    query = QueryDict(mutable=True)
    for k, v in kwargs.items():
        query[k] = v
    return f"?{query.urlencode()}"
