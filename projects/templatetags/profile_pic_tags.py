from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def profile_image(scientist):
    if scientist:
        if getattr(scientist, "profile_picture", None):
            try:
                return scientist.profile_picture.url
            except:
                pass

        if getattr(scientist, "profile_picture_url", None):
            return scientist.profile_picture_url

    return static("images/no_profile_image.png")