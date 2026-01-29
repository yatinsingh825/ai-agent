import logging
from typing import Dict, Any
from services.external_service import ExternalService
from exceptions.custom_exceptions import ServiceUnavailableError
from config.config import Config

logger = logging.getLogger(__name__)


class ElevenLabsService(ExternalService):
    def __init__(self, simulate_failure: bool = False):
        super().__init__("ElevenLabs")
        self.api_url = Config.ELEVENLABS_API_URL
        self.simulate_failure = simulate_failure
        self.call_count = 0
    
    def text_to_speech(self, text: str, voice_id: str = "default") -> Dict[str, Any]:
        """Convert text to speech"""
        self.call_count += 1
        
        # Simulate 503 error for testing
        if self.simulate_failure and self.call_count <= 3:
            logger.info(f"{self.service_name}: Simulating 503 error (call #{self.call_count})")
            raise ServiceUnavailableError(
                self.service_name, 
                "Service unavailable (503)", 
                None
            )
        
        # Normal successful response
        logger.info(f"{self.service_name}: Making text-to-speech request")
        return {
            "audio_url": f"https://mock-audio-url.com/{voice_id}",
            "duration": 5.2,
            "status": "success"
        }
    
    def health_check(self) -> bool:
        """Check if service is healthy"""
        try:
            # After 3 failures, simulate recovery
            if self.simulate_failure and self.call_count > 3:
                self.simulate_failure = False
                logger.info(f"{self.service_name}: Service recovered")
                return True
            
            if self.simulate_failure:
                return False
            
            return True
        except Exception:
            return False
