import sendgrid
import os
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content
load_dotenv()

def send_email(from_email, to_email, subject,content):
   
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

    mail = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject=subject,
        plain_text_content = Content("text/html", content)
    )
    mail_json = mail.get()

    response = sg.client.mail.send.post(request_body=mail_json)
    return response.status_code