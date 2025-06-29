from django.conf import settings
from common.email import compose_and_send_email
from celery import shared_task
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User

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
