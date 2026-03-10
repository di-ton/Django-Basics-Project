from django.db import models

from common.models import TimeStampedModel
from sciProSpace import settings


class Message(TimeStampedModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="received_messages",
        through="MessageRecipient",
    )

    project = models.ForeignKey(
        "projects.Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="messaging"
    )

    subject = models.CharField(max_length=255)
    body = models.TextField()

    @property
    def is_project_message(self):
        return self.project is not None


class MessageRecipient(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ("message", "recipient")


