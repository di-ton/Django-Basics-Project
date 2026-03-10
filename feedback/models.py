from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from common.models import TimeStampedModel


class Comment(TimeStampedModel):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )



    def clean(self):
        if self.parent and self.parent.parent:
            raise ValidationError("Only one level of replies allowed.")
