from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver

from users.helpers import notifications
from users.models import Notification, RegistrationApplication, UserProfile
from blogs.models import Blog
from .helpers.users import approve_application, reject_application


@receiver(pre_save, sender=RegistrationApplication)
def on_registration_application_change(sender, instance: RegistrationApplication, **kwargs):
    """Signal that checks if the application's status was changed.
    If the application was not saved before, it does nothing.
    If the application was previously saved, and the new status is
    "Approved", then it calls the `approve_application` function."""
    if instance.was_ever_reviewed:
        return None

    # if the application was not previously created
    if not instance.pk:
        return None

    # else...
    previous_instance = RegistrationApplication.objects.get(pk=instance.pk)

    # if there was a change and the client has been approved or rejected
    if previous_instance.status != instance.status == 1:
        approve_application(user=instance.user)
    elif previous_instance.status != instance.status == 2:
        reject_application(user=instance.user)


post_save.connect(notifications.on_new_blog, sender=Blog)
m2m_changed.connect(notifications.on_like, sender=Blog.likes.through)
m2m_changed.connect(notifications.on_subscription, sender=UserProfile.subscriptions.through)
