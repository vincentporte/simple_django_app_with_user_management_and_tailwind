from django import template
from django.forms.widgets import DateInput, Select, Textarea

register = template.Library()


@register.filter
def is_select(field):
    if isinstance(field.field.widget, Select):
        return True
    else:
        return False


@register.filter
def is_dateinput(field):
    if isinstance(field.field.widget, DateInput):
        return True
    else:
        return False


@register.filter
def is_textarea(field):
    if isinstance(field.field.widget, Textarea):
        return True
    else:
        return False
