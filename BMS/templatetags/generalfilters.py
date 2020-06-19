from django import template
register = template.Library()

a = None

@register.filter
def get_item(dictionary, key):
    global a
    a = key
    return dictionary.get(key)

@register.filter
def add_item(value,b):
    # print('%^&*')
    # print(a)
    # print(value)
    # print(b)
    return value + b[a]