from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User

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


def compose_and_send_email(user_id: int, subject: str, template_name: str, extra_context=None):
    """Get the User ID, subject of the email and the name of the template that
    containts the email. The `User` and `settings` instances are included in 
    the context by default."""
    
    if extra_context is None:
        extra_context = {}
    
    user = User.objects.get(pk=user_id)
    
    context = {'settings': settings,
               'user': user,
               **extra_context}
    
    email = EmailMessage(subject=subject, 
                         body=render_to_string(template_name=template_name, context=context))
    
    send_email_to_user(email_message=email, user=user)
