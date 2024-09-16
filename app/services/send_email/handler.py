from email.message import EmailMessage
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr
from app.config import settings


def create_status_change_mail_template(email_to: EmailStr, task_data: dict) -> EmailMessage:
    """Creates an email with a status change notification using a Jinja2 template.

    Args:
        email_to (EmailStr): Recipient email address.
        task_data (dict): Data containing task details like task ID and status.

    Returns:
        EmailMessage: The constructed email message with HTML content.
    """
    # Set up the Jinja2 environment to load templates from the 'templates' directory
    template_dir = Path(__file__).parent / 'templates'
    env = Environment(loader=FileSystemLoader(template_dir))

    # Load and render the HTML email template
    template = env.get_template('email_template.html')
    rendered_html = template.render(**task_data)

    # Create the email message
    email = EmailMessage()
    email["Subject"] = f"Status of Task {task_data['id']} was Changed to {task_data['status']}"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    # Set the HTML content in the email
    email.set_content(rendered_html, subtype="html")

    return email


def mock_create_status_change_mail_template(email_message: EmailMessage):
    """Saves the email as an HTML file in the 'mock_mail' directory for debugging purposes.

    Args:
        email_message (EmailMessage): The email message to save as an HTML file.
    """
    # Create the 'mock_mail' directory if it doesn't exist
    mock_mail_dir = Path(__file__).parent / 'mock_mail'
    mock_mail_dir.mkdir(exist_ok=True)

    # Generate a unique file name based on the email subject
    subject = email_message['Subject'].replace(" ", "_").replace("#", "").replace(":", "")
    file_path = mock_mail_dir / f"{subject}.html"

    # Write the HTML content to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(email_message.get_content())

    print(f"Mock email saved to {file_path}")
