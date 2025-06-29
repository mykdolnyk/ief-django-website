from django.conf import settings
from common.email import compose_and_send_email
from celery import shared_task
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User

from users.models import UserProfile
from users.helpers.users import update_pfp

@shared_task
def send_registration_confirmation_email(user_id: int):
    """Celery task responsible for sending a registration confirmation email."""
    compose_and_send_email(user_id,
                           "Your Application has been Submitted",
                           'email/application_submitted.html')

@shared_task
def send_application_approval_email(user_id: int):
    """Celery task responsible for sending a registration approval email."""
    compose_and_send_email(user_id,
                           "Your Application has been Approved",
                           'email/application_approved.html')

@shared_task
def send_application_rejection_email(user_id: int):
    """Celery task responsible for sending a registration rejection email."""
    compose_and_send_email(user_id,
                           "Your Application has been Rejected",
                           'email/application_rejected.html')

@shared_task
def send_password_reset_email(subject_template_name, email_template_name,
                              context, from_email, to_email, html_email_template_name):
    """Celery task responsible for sending a password reset email. Should be called by the
    `users.forms.PasswordResetEmailForm` form class."""
    
    context['user'] = User.objects.get(pk=context["user"]) # "unpack" the user from an ID
    
    # Some witchcraft to pass the settings obj into the task:
    if context['settings'] is True:
        context['settings'] = settings
    
    return PasswordResetForm.send_mail(None,
        subject_template_name, email_template_name, 
        context, from_email, to_email, html_email_template_name)


@shared_task
def update_single_pfp_task(profile_id: int):
    """Celery task to update a PFP of a single user profile."""
    profile = UserProfile.objects.get(pk=profile_id)
    update_pfp(profile)
    

@shared_task
def update_every_pfp_task(delay=5):
    """Celery task to update PFP of every active user's profile.

    Args:
        delay (int, optional): Period (in seconds) between every single PFP update. Defaults to 5.
    """
    active_user_profiles = UserProfile.objects.filter(user__is_active=True)
    
    for index, profile in enumerate(active_user_profiles):
        # Queue all the tasks, make them run one by one every `delay` seconds
        update_single_pfp_task.apply_async(args=[profile.pk], countdown=(delay * index))