import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
from core.retry_handler import RetryHandler
from core.circuit_breaker import CircuitBreaker
from services.elevenlabs_service import ElevenLabsService
from exceptions.custom_exceptions import TransientError, CircuitBreakerOpenError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_complete_503_scenario():
    """Test the complete ElevenLabs 503 scenario as per requirements"""
    print("\n" + "=" * 70)
    print("TESTING COMPLETE 503 SCENARIO (As Per Assignment Requirements)")
    print("=" * 70)
    
    # Initialize components
    elevenlabs_service = ElevenLabsService(simulate_failure=True)
    retry_handler = RetryHandler(initial_delay=2, max_attempts=3, backoff_multiplier=2)
    circuit_breaker = CircuitBreaker("ElevenLabs", failure_threshold=3, timeout=10)
    
    contact_queue = [
        {"id": 1, "name": "Contact 1"},
        {"id": 2, "name": "Contact 2"},
        {"id": 3, "name": "Contact 3"},
    ]
    
    print("\n--- Processing Contact Queue ---\n")
    
    for contact in contact_queue:
        print(f"\n{'='*70}")
        print(f"Processing: {contact['name']}")
        print(f"{'='*70}")
        
        try:
            # Attempt call with retry + circuit breaker
            result = circuit_breaker.call(
                lambda: retry_handler.execute_with_retry(
                    elevenlabs_service.text_to_speech,
                    "ElevenLabs",
                    f"Hello {contact['name']}"
                )
            )
            
            print(f"✓ Call to {contact['name']} SUCCESS")
            print(f"  Result: {result}")
            
        except CircuitBreakerOpenError as e:
            print(f"✗ Circuit Breaker OPEN - Failing fast for {contact['name']}")
            print(f"  Moving to next contact...")
            
        except TransientError as e:
            print(f"✗ Call to {contact['name']} FAILED after retries")
            print(f"  Error: {e}")
            print(f"  Triggering alert to admin...")
            print(f"  Moving to next contact in queue...")
            
        except Exception as e:
            print(f"✗ Unexpected error for {contact['name']}: {e}")
        
        print(f"Circuit Breaker State: {circuit_breaker.get_state()}")
        print(f"Service Health: {elevenlabs_service.health_check()}")
        
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("SCENARIO TEST COMPLETED")
    print("=" * 70)
    print(f"\nFinal Circuit Breaker State: {circuit_breaker.get_state()}")
    print(f"Final Service Health: {elevenlabs_service.health_check()}")


if __name__ == "__main__":
    test_complete_503_scenario()
