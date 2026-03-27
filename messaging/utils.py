from django.contrib.auth import get_user_model

from .models import MessageRecipient
from django.core.mail import send_mail
from django.conf import settings
import asyncio
from asgiref.sync import sync_to_async


def unread_messages_count(user):
    if not user.is_authenticated:
        return 0

    return MessageRecipient.objects.filter(
        recipient=user,
        is_read=False
    ).count()


User = get_user_model()

def notify_moderators_about_report(project, message, sender):
    moderators = User.objects.filter(groups__name="Content Moderators")

    emails = [user.email for user in moderators if user.email]

    if not emails:
        return

    send_mail(
        subject=f"New Project Report: {project.title}",
        message=(
            f"A new issue has been reported.\n\n"
            f"Project: {project.title}\n"
            f"Reported by: {sender.email}\n\n"
            f"Message:\n{message.body}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )



# async def notify_moderators_about_report_async(project, message, sender):
#     await sync_to_async(notify_moderators_about_report)(
#         project, message, sender
#     )

