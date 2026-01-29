import requests
import logging
from config.config import Config

logger = logging.getLogger(__name__)


class WebhookAlert:
    def __init__(self):
        self.webhook_url = Config.WEBHOOK_URL
    
    def send_alert(self, payload: dict):
        """Send webhook alert"""
        if not self.webhook_url:
            logger.warning("Webhook URL not configured, skipping webhook alert")
            logger.info(f"[WEBHOOK ALERT] {payload}")
            return
        
        try:
            logger.info(f"Webhook alert sent to {self.webhook_url}")
        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
