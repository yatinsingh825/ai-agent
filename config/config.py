import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Retry Configuration
    RETRY_INITIAL_DELAY = 5
    RETRY_MAX_ATTEMPTS = 3
    RETRY_BACKOFF_MULTIPLIER = 2
    
    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
    CIRCUIT_BREAKER_TIMEOUT = 60
    CIRCUIT_BREAKER_HALF_OPEN_ATTEMPTS = 1
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL = 30
    HEALTH_CHECK_TIMEOUT = 5
    
    # Logging Configuration
    LOG_FILE_PATH = "logs/error_logs.json"
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDS", "credentials.json")
    GOOGLE_SHEETS_NAME = os.getenv("GOOGLE_SHEETS_NAME", "Error Recovery Logs")
    
    # Alert Configuration
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    
    # Service URLs
    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
    LLM_API_URL = "https://api.openai.com/v1/chat/completions"
