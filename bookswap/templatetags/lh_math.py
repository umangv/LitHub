from django import template

register = template.Library()

@register.filter
def mod(x, n):
    return int(x) % int(n)
