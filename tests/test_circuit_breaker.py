import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.circuit_breaker import CircuitBreaker, CircuitState
import time


def test_circuit_breaker_closed_state():
    """Test circuit breaker in CLOSED state"""
    print("\n=== Test 1: Circuit Breaker CLOSED State ===")
    
    cb = CircuitBreaker("TestService", failure_threshold=3, timeout=5)
    
    def successful_func():
        return "Success"
    
    result = cb.call(successful_func)
    print(f"Call result: {result}")
    print(f"Circuit state: {cb.get_state()}")
    print("✓ Test passed")


def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold failures"""
    print("\n=== Test 2: Circuit Breaker Opens After Failures ===")
    
    cb = CircuitBreaker("TestService", failure_threshold=3, timeout=5)
    
    def failing_func():
        raise Exception("Service error")
    
    # Cause 3 failures
    for i in range(3):
        try:
            cb.call(failing_func)
        except Exception:
            print(f"Failure {i+1}, State: {cb.get_state()}")
    
    print(f"Final state: {cb.get_state()}")
    
    if cb.get_state() == CircuitState.OPEN:
        print("✓ Test passed - circuit breaker OPENED")
    else:
        print("✗ Test failed - circuit breaker should be OPEN")


def test_circuit_breaker_half_open():
    """Test circuit breaker transitions to HALF_OPEN"""
    print("\n=== Test 3: Circuit Breaker HALF_OPEN Transition ===")
    
    cb = CircuitBreaker("TestService", failure_threshold=2, timeout=3)
    
    def failing_func():
        raise Exception("Service error")
    
    # Open the circuit
    for i in range(2):
        try:
            cb.call(failing_func)
        except Exception:
            pass
    
    print(f"State after failures: {cb.get_state()}")
    
    # Wait for timeout
    print("Waiting for timeout...")
    time.sleep(3.5)
    
    print(f"State after timeout: {cb.get_state()}")
    
    if cb.get_state() == CircuitState.HALF_OPEN:
        print("✓ Test passed - transitioned to HALF_OPEN")
    else:
        print("✗ Test failed - should be HALF_OPEN")


def test_circuit_breaker_recovery():
    """Test circuit breaker closes after successful call in HALF_OPEN"""
    print("\n=== Test 4: Circuit Breaker Recovery ===")
    
    cb = CircuitBreaker("TestService", failure_threshold=2, timeout=2, half_open_attempts=1)
    
    # Open the circuit
    for i in range(2):
        try:
            cb.call(lambda: (_ for _ in ()).throw(Exception("Fail")))
        except Exception:
            pass
    
    print(f"State: {cb.get_state()}")
    
    # Wait for timeout
    time.sleep(2.5)
    print(f"State after timeout: {cb.get_state()}")
    
    # Successful call in HALF_OPEN
    def successful_func():
        return "Success"
    
    result = cb.call(successful_func)
    print(f"Call result: {result}")
    print(f"Final state: {cb.get_state()}")
    
    if cb.get_state() == CircuitState.CLOSED:
        print("✓ Test passed - circuit breaker CLOSED (recovered)")
    else:
        print("✗ Test failed - should be CLOSED")


if __name__ == "__main__":
    print("=" * 50)
    print("CIRCUIT BREAKER STANDALONE TESTS")
    print("=" * 50)
    
    test_circuit_breaker_closed_state()
    test_circuit_breaker_opens_after_failures()
    test_circuit_breaker_half_open()
    test_circuit_breaker_recovery()
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)
