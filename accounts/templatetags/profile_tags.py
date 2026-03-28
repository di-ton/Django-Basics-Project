from django import template

register = template.Library()

@register.filter
def has_profile(user):
    return hasattr(user, 'scientist_profile')