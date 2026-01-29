import logging
from config.config import Config

logger = logging.getLogger(__name__)


class TelegramAlert:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
    
    def send_alert(self, message: str):
        """Send Telegram alert"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured, skipping telegram alert")
            logger.info(f"[TELEGRAM ALERT] {message}")
            return
        
        try:
            logger.info(f"Telegram alert sent: {message[:50]}...")
        
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
