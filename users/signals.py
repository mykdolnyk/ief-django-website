from django.db.models.signals import pre_save
from django.dispatch import receiver

from users.models import RegistrationApplication
from .helpers.users import approve_application, reject_application
from helpers.email import send_application_rejection_email


@receiver(pre_save, sender=RegistrationApplication)
def on_registration_application_change(sender, instance:RegistrationApplication, **kwargs):
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