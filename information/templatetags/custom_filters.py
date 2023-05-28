from django import template

register = template.Library()

@register.filter
def split_by(value, delimiter):
    return value.split(delimiter)
