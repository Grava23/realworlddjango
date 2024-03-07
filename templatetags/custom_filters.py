from django import template

register = template.Library()

@register.filter
def add_attr(field, attrs):
    attrs = attrs.split(',')
    for attr in attrs:
        attr_name, attr_value = attr.split(':')
        field.field.widget.attrs[attr_name] = attr_value
    return field
