import smtplib
from pydantic import EmailStr
from app.config import settings
from app.services.celery_app import celery
from app.services.send_email.handler import (
    create_status_change_mail_template,
    mock_create_status_change_mail_template
)


@celery.task
def send_task_update_status_email(email_to: EmailStr, task_data: dict):
    """Celery task to send a task status update email.

    Args:
        email_to (EmailStr): Recipient email address.
        task_data (dict): Task details including task ID and status.
    """
    # Generate the email content using the template
    msg_message = create_status_change_mail_template(email_to=email_to, task_data=task_data)

    if settings.DEBUG:
        # Save the email as an HTML file in 'mock_mail' when in debug mode
        mock_create_status_change_mail_template(msg_message)
    else:
        # Send the email via SMTP in production mode
        try:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg_message)
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
