from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.mail import send_mail

from accounts.models import ScientistProfile
from sciProSpace import settings

import cloudinary.uploader



@receiver(post_save, sender=ScientistProfile)
def notify_moderators_on_profile_creation(sender, instance, created, **kwargs):
    if created:
        try:
            moderators = Group.objects.get(
                name="Profile Moderators"
            ).user_set.all()

            for moderator in moderators:
                if moderator.email:
                    send_mail(
                        subject="New Profile Created",
                        message=(
                            f"A new profile has been created:\n\n"
                            f"Name: {instance.full_name}\n"
                            f"Email: {instance.user.email}\n"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[moderator.email],
                        fail_silently=False,
                    )

        except Group.DoesNotExist:
            pass



@receiver(post_delete, sender=ScientistProfile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        cloudinary.uploader.destroy(instance.profile_picture.public_id)


@receiver(pre_save, sender=ScientistProfile)
def delete_old_picture(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_picture = ScientistProfile.objects.get(pk=instance.pk).profile_picture
    except ScientistProfile.DoesNotExist:
        return

    if old_picture and old_picture != instance.profile_picture:
        cloudinary.uploader.destroy(old_picture.public_id)