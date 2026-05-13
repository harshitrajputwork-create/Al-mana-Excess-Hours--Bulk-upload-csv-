import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class EmailSender:
    def __init__(self, smtp_cfg):
        self.smtp_server = smtp_cfg.get('smtp_server')
        self.smtp_port = smtp_cfg.get('smtp_port')
        self.smtp_user = smtp_cfg.get('smtp_user')
        self.smtp_pass = smtp_cfg.get('smtp_pass')
        self.sender_email = smtp_cfg.get('sender') or self.smtp_user

    def send(self, recipient_email, subject, html_content):
        """
        Sends an HTML email to the recipient.
        """
        if not self.smtp_server or not self.smtp_user or not self.smtp_pass:
            logging.warning("SMTP configuration is incomplete. Skipping email delivery.")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = recipient_email

        part = MIMEText(html_content, "html")
        message.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            logging.info(f"Successfully sent email to {recipient_email}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
