from django import template


register = template.Library()


@register.filter
def add_class(field, new_class):
    yet_class = field.field.widget.attrs.get('class', '')
    field.field.widget.attrs['class'] = yet_class + new_class
    return field


@register.filter
def add_placeholder(field, placeholder):
    field.field.widget.attrs['placeholder'] = placeholder
    return field