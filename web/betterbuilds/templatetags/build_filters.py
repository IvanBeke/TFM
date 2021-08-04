from django import template


register = template.Library()


@register.filter('percentage')
def get_percentage(value, arg):
    return round(value / arg * 100, 2)
