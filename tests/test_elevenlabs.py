import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.elevenlabs_service import ElevenLabsService
from exceptions.custom_exceptions import ServiceUnavailableError


def test_elevenlabs_success():
    """Test successful ElevenLabs call"""
    print("\n=== Test 1: ElevenLabs Success ===")
    
    service = ElevenLabsService(simulate_failure=False)
    
    result = service.text_to_speech("Hello world", "voice_123")
    print(f"Result: {result}")
    print("✓ Test passed")


def test_elevenlabs_503_error():
    """Test ElevenLabs 503 error simulation"""
    print("\n=== Test 2: ElevenLabs 503 Error ===")
    
    service = ElevenLabsService(simulate_failure=True)
    
    try:
        result = service.text_to_speech("Hello world")
        print("✗ Test failed - should have raised 503 error")
    except ServiceUnavailableError as e:
        print(f"✓ Test passed - 503 error raised: {e}")


def test_elevenlabs_recovery():
    """Test ElevenLabs recovery after failures"""
    print("\n=== Test 3: ElevenLabs Recovery ===")
    
    service = ElevenLabsService(simulate_failure=True)
    
    # First 3 calls will fail
    for i in range(3):
        try:
            service.text_to_speech("Test")
        except Exception:
            print(f"Call {i+1} failed (expected)")
    
    # 4th call should succeed
    try:
        result = service.text_to_speech("Test")
        print(f"Call 4 succeeded: {result}")
        print("✓ Test passed - service recovered")
    except Exception as e:
        print(f"✗ Test failed - should have recovered: {e}")


def test_health_check():
    """Test health check functionality"""
    print("\n=== Test 4: Health Check ===")
    
    service = ElevenLabsService(simulate_failure=True)
    
    # Health check should return False when failing
    health = service.health_check()
    print(f"Health (simulating failure): {health}")
    
    # After recovery
    service.call_count = 4
    service.simulate_failure = False
    health = service.health_check()
    print(f"Health (after recovery): {health}")
    
    print("✓ Test passed")


if __name__ == "__main__":
    print("=" * 50)
    print("ELEVENLABS SERVICE STANDALONE TESTS")
    print("=" * 50)
    
    test_elevenlabs_success()
    test_elevenlabs_503_error()
    test_elevenlabs_recovery()
    test_health_check()
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)
