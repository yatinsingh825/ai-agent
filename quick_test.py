print("Testing imports...")

try:
    from config.config import Config
    print("✓ config.config imported")
except Exception as e:
    print(f"✗ config.config failed: {e}")

try:
    from exceptions.custom_exceptions import TransientError
    print("✓ exceptions imported")
except Exception as e:
    print(f"✗ exceptions failed: {e}")

try:
    from core.retry_handler import RetryHandler
    print("✓ core.retry_handler imported")
except Exception as e:
    print(f"✗ core.retry_handler failed: {e}")

try:
    from services.elevenlabs_service import ElevenLabsService
    print("✓ services.elevenlabs_service imported")
except Exception as e:
    print(f"✗ services.elevenlabs_service failed: {e}")

print("\n✅ All imports successful!" if all else "❌ Some imports failed")
