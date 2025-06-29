from common.email import compose_and_send_email
from celery import shared_task


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

