from .models import MessageRecipient


def unread_messages_count(user):
    if not user.is_authenticated:
        return 0

    return MessageRecipient.objects.filter(
        recipient=user,
        is_read=False
    ).count()