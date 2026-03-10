from .utils import unread_messages_count


def unread_messages(request):
    return {
        "unread_messages_count": unread_messages_count(request.user)
    }