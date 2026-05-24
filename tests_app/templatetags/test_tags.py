from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def percentage(value, total):
    if total:
        return round(value / total * 100)
    return 0
