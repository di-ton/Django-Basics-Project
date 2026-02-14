from django import template
from django.utils.dateformat import format

register = template.Library()

@register.simple_tag
def event_meta(event):
    parts = []

    if event.location:
        parts.append(event.location)

    if event.start_date:
        start = format(event.start_date, "d.m.Y")

        if event.end_date:
            end = format(event.end_date, "d.m.Y")
            parts.append(f"{start} - {end}")
        else:
            parts.append(start)

    return " · ".join(parts)
