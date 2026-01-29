import logging
import time
from typing import Dict, Any

from config.config import Config
from core.retry_handler import RetryHandler
from core.circuit_breaker import CircuitBreaker, CircuitState
from core.health_check import HealthCheckManager
from services.elevenlabs_service import ElevenLabsService
from services.llm_service import LLMService
from loggers.file_logger import FileLogger
from loggers.sheets_logger import SheetsLogger
from alerts.email_alert import EmailAlert
from alerts.telegram_alert import TelegramAlert
from alerts.webhook_alert import WebhookAlert
from exceptions.custom_exceptions import (
    ServiceException, TransientError, PermanentError, CircuitBreakerOpenError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AICallAgent:
    def __init__(self):
        # Initialize services
        self.elevenlabs_service = ElevenLabsService(simulate_failure=False)
        self.llm_service = LLMService()
        
        # Initialize retry handler
        self.retry_handler = RetryHandler()
        
        # Initialize circuit breakers
        self.circuit_breakers = {
            "ElevenLabs": CircuitBreaker("ElevenLabs"),
            "LLM": CircuitBreaker("LLM")
        }
        
        # Initialize health check manager
        self.health_check_manager = HealthCheckManager()
        self.health_check_manager.register_service(
            "ElevenLabs",
            self.elevenlabs_service.health_check
        )
        self.health_check_manager.register_service(
            "LLM",
            self.llm_service.health_check
        )
        
        # Initialize loggers
        self.file_logger = FileLogger(Config.LOG_FILE_PATH)
        self.sheets_logger = SheetsLogger(
            Config.GOOGLE_SHEETS_CREDENTIALS_FILE,
            Config.GOOGLE_SHEETS_NAME
        )
        
        # Initialize alert systems
        self.email_alert = EmailAlert()
        self.telegram_alert = TelegramAlert()
        self.webhook_alert = WebhookAlert()
    
    def make_single_call(self, contact: Dict[str, Any], simulate_503: bool = False):
        """Make a single call to a contact"""
        print("\n" + "="*70)
        print(f"Processing Contact: {contact['name']}")
        print("="*70)
        
        # Set simulation flag
        if simulate_503:
            self.elevenlabs_service.simulate_failure = True
            self.elevenlabs_service.call_count = 0
        
        try:
            # Step 1: Generate LLM response
            print("\n[Step 1] Generating LLM response...")
            llm_response = self.call_with_resilience(
                "LLM",
                self.llm_service.generate_response,
                [{"role": "user", "content": f"Call script for {contact['name']}"}]
            )
            print(f"✓ LLM Response: {llm_response['response']}")
            
            # Step 2: Convert text to speech
            print(f"\n[Step 2] Converting to speech using ElevenLabs...")
            tts_response = self.call_with_resilience(
                "ElevenLabs",
                self.elevenlabs_service.text_to_speech,
                llm_response['response']
            )
            print(f"✓ Audio URL: {tts_response['audio_url']}")
            print(f"✓ Duration: {tts_response['duration']}s")
            
            print("\n" + "="*70)
            print(f"✅ CALL TO {contact['name']} COMPLETED SUCCESSFULLY")
            print("="*70)
            
            return {
                "contact": contact,
                "llm_response": llm_response,
                "tts_response": tts_response,
                "status": "success"
            }
        
        except CircuitBreakerOpenError as e:
            print(f"\n❌ Circuit Breaker OPEN - Failing fast")
            print(f"   Error: {e}")
            self.send_critical_alert(
                f"Circuit Breaker Opened for ElevenLabs",
                f"The circuit breaker is OPEN. Service is unavailable."
            )
            print("\n" + "="*70)
            print(f"❌ CALL TO {contact['name']} FAILED (Circuit Breaker Open)")
            print("="*70)
            raise
        
        except TransientError as e:
            print(f"\n❌ Transient error after all retries")
            print(f"   Error: {e}")
            self.send_critical_alert(
                f"ElevenLabs Call Failed Permanently",
                f"Call failed after {Config.RETRY_MAX_ATTEMPTS} retries.\nError: {e}"
            )
            print("\n" + "="*70)
            print(f"❌ CALL TO {contact['name']} FAILED (Max Retries Exceeded)")
            print("="*70)
            raise
        
        except PermanentError as e:
            print(f"\n❌ Permanent error (no retry)")
            print(f"   Error: {e}")
            self.send_critical_alert(
                f"ElevenLabs Permanent Error",
                f"Permanent error: {e}"
            )
            print("\n" + "="*70)
            print(f"❌ CALL TO {contact['name']} FAILED (Permanent Error)")
            print("="*70)
            raise
    
    def call_with_resilience(self, service_name: str, func, *args, **kwargs):
        """Call a service with full resilience (retry + circuit breaker)"""
        circuit_breaker = self.circuit_breakers[service_name]
        
        # Execute with retry logic wrapped in circuit breaker
        result = circuit_breaker.call(
            lambda: self.retry_handler.execute_with_retry(
                func,
                service_name,
                *args,
                **kwargs
            )
        )
        
        # Log success
        self.log_event(
            service_name=service_name,
            error_category="SUCCESS",
            retry_count=0,
            circuit_breaker_state=circuit_breaker.get_state().value,
            message=f"Call to {service_name} succeeded"
        )
        
        return result
    
    def log_event(self, service_name: str, error_category: str, 
                  retry_count: int, circuit_breaker_state: str, message: str):
        """Log event to all logging channels"""
        self.file_logger.log_event(
            service_name, error_category, retry_count, 
            circuit_breaker_state, message
        )
        self.sheets_logger.log_event(
            service_name, error_category, retry_count, 
            circuit_breaker_state, message
        )
    
    def send_critical_alert(self, subject: str, message: str):
        """Send alerts through all channels"""
        self.email_alert.send_alert(subject, message)
        self.telegram_alert.send_alert(f"{subject}\n\n{message}")
        self.webhook_alert.send_alert({
            "subject": subject,
            "message": message,
            "timestamp": time.time()
        })
    
    def get_circuit_breaker_status(self):
        """Display circuit breaker status"""
        print("\n" + "="*70)
        print("CIRCUIT BREAKER STATUS")
        print("="*70)
        for service, cb in self.circuit_breakers.items():
            state = cb.get_state()
            print(f"{service:20} : {state.value}")
        print("="*70)
    
    def reset_circuit_breakers(self):
        """Reset all circuit breakers"""
        for service, cb in self.circuit_breakers.items():
            cb.reset()
        print("\n✓ All circuit breakers reset to CLOSED state")


def show_menu():
    """Display interactive menu"""
    print("\n" + "="*70)
    print("AI CALL AGENT - ERROR RECOVERY & RESILIENCE SYSTEM")
    print("="*70)
    print("\n[1] Make Normal Call (Success scenario)")
    print("[2] Simulate 503 Error (With Retry & Recovery)")
    print("[3] View Circuit Breaker Status")
    print("[4] Reset Circuit Breakers")
    print("[5] Run Complete 503 Scenario (Assignment Demo)")
    print("[6] Exit")
    print("\n" + "="*70)


def main():
    """Main entry point with interactive menu"""
    agent = AICallAgent()
    
    # Sample contacts
    contacts = [
        {"id": 1, "name": "Alice Johnson", "phone": "+1234567890"},
        {"id": 2, "name": "Bob Smith", "phone": "+1234567891"},
        {"id": 3, "name": "Charlie Brown", "phone": "+1234567892"},
    ]
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            # Normal successful call
            print("\n📞 Making Normal Call...")
            contact = {"name": "John Doe", "phone": "+1234567890"}
            try:
                agent.make_single_call(contact, simulate_503=False)
            except Exception as e:
                logger.error(f"Call failed: {e}")
        
        elif choice == "2":
            # Simulate 503 error
            print("\n⚠️  Simulating 503 Service Unavailable Error...")
            contact = {"name": "Jane Smith", "phone": "+1234567891"}
            try:
                agent.make_single_call(contact, simulate_503=True)
            except Exception as e:
                logger.error(f"Call failed as expected: {e}")
        
        elif choice == "3":
            # View circuit breaker status
            agent.get_circuit_breaker_status()
        
        elif choice == "4":
            # Reset circuit breakers
            agent.reset_circuit_breakers()
        
        elif choice == "5":
            # Run complete scenario (as per assignment)
            print("\n" + "="*70)
            print("RUNNING COMPLETE 503 SCENARIO (Assignment Requirement)")
            print("="*70)
            print("\nThis will demonstrate:")
            print("  1. 503 error detection")
            print("  2. Retry with exponential backoff (5s, 10s, 20s)")
            print("  3. Alert triggering")
            print("  4. Moving to next contact")
            print("  5. Service recovery")
            print("  6. Successful subsequent calls")
            print("\n" + "="*70)
            
            input("\nPress Enter to start...")
            
            # Reset first
            agent.reset_circuit_breakers()
            agent.elevenlabs_service.call_count = 0
            
            for i, contact in enumerate(contacts, 1):
                print(f"\n\n{'='*70}")
                print(f"CONTACT {i} of {len(contacts)}")
                print(f"{'='*70}")
                
                # First contact will fail (503), rest will succeed
                simulate_503 = (i == 1)
                
                try:
                    agent.make_single_call(contact, simulate_503=simulate_503)
                except Exception:
                    print(f"\n→ Moving to next contact...")
                
                if i < len(contacts):
                    print("\nWaiting 2 seconds before next contact...")
                    time.sleep(2)
            
            print("\n" + "="*70)
            print("✅ COMPLETE SCENARIO FINISHED")
            print("="*70)
            print("\nCheck logs/error_logs.json for detailed logs")
        
        elif choice == "6":
            print("\n👋 Exiting AI Call Agent. Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 1-6.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
