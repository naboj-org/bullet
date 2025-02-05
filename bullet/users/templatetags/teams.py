from django import template

register = template.Library()


@register.inclusion_tag("partials/team_name.html")
def full_team_name(team):
    return {"team": team}


@register.inclusion_tag("partials/team_name_inline.html")
def inline_team_name(team):
    return {"team": team}
