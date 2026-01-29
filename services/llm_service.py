import logging
from typing import Dict, Any, List
from services.external_service import ExternalService
from config.config import Config

logger = logging.getLogger(__name__)


class LLMService(ExternalService):
    def __init__(self):
        super().__init__("LLM")
        self.api_url = Config.LLM_API_URL
    
    def generate_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate LLM response"""
        try:
            logger.info(f"{self.service_name}: Generating response")
            return {
                "response": "This is a mock LLM response",
                "tokens_used": 150,
                "status": "success"
            }
        except Exception as e:
            self.handle_exception(e)
    
    def health_check(self) -> bool:
        """Check if service is healthy"""
        try:
            return True
        except Exception:
            return False
