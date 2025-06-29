from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
# from .tasks import send_email_to_user

def send_email_to_user(email_message: EmailMessage, user:User=None):
    """Send an email to the user's email address set in the account.
    If the EmailMessage object doesn't have the 'to' value specified,
    the user will be appended automatically."""
    
    if user.email not in email_message.to:
        # Include the user's email in the "to" field
        email_message.to.append(user.email)

    email = email_message
    email.content_subtype = "html"
    
    return email.send()


def send_registration_confirmation_email(user: User):
    context = {'settings': settings,
               'user': user}
    email = EmailMessage("Your Application has been Submitted",
                         render_to_string('email/application_submitted.html', context=context))
    send_email_to_user.delay(email_message=email, user=user)


def send_application_approval_email(user: User):
    context = {'settings': settings,
               'user': user}
    email = EmailMessage("Your Application has been Approved",
                         render_to_string('email/application_approved.html', context=context))
    send_email_to_user.delay(email_message=email, user=user).delay()


def send_application_rejection_email(user: User):
    context = {'settings': settings,
               'user': user}
    email = EmailMessage("Your Application has been Rejected",
                         render_to_string('email/application_rejected.html', context=context))
    send_email_to_user.delay(email_message=email, user=user).delay()
