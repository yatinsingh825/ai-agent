import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config.config import Config

logger = logging.getLogger(__name__)


class EmailAlert:
    def __init__(self):
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.sender = Config.EMAIL_SENDER
        self.password = Config.EMAIL_PASSWORD
        self.receiver = Config.EMAIL_RECEIVER
    
    def send_alert(self, subject: str, message: str):
        """Send email alert"""
        if not self.sender or not self.receiver:
            logger.warning("Email credentials not configured, skipping email alert")
            logger.info(f"[EMAIL ALERT] {subject}: {message}")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = self.receiver
            msg['Subject'] = f"[AI Call Agent Alert] {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            logger.info(f"Email alert sent: {subject}")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
