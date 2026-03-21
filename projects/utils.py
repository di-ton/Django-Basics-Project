def is_content_moderator(user):
    return user.groups.filter(name="Content Moderators").exists()