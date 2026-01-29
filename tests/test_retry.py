import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.retry_handler import RetryHandler
from exceptions.custom_exceptions import TransientError, PermanentError
import time


def test_successful_call():
    """Test successful call without retry"""
    print("\n=== Test 1: Successful Call ===")
    
    retry_handler = RetryHandler()
    
    def successful_func():
        print("Function executed successfully")
        return "Success"
    
    result = retry_handler.execute_with_retry(successful_func, "TestService")
    print(f"Result: {result}")
    print("✓ Test passed")


def test_transient_error_with_retry():
    """Test transient error with successful retry"""
    print("\n=== Test 2: Transient Error with Retry ===")
    
    retry_handler = RetryHandler(initial_delay=1, max_attempts=3)
    
    attempt_count = [0]
    
    def transient_failure_func():
        attempt_count[0] += 1
        print(f"Attempt {attempt_count[0]}")
        
        if attempt_count[0] < 3:
            raise TransientError("TestService", f"Transient error on attempt {attempt_count[0]}")
        
        return "Success after retries"
    
    try:
        result = retry_handler.execute_with_retry(transient_failure_func, "TestService")
        print(f"Result: {result}")
        print("✓ Test passed - succeeded after retries")
    except Exception as e:
        print(f"✗ Test failed: {e}")


def test_permanent_error_no_retry():
    """Test permanent error (should not retry)"""
    print("\n=== Test 3: Permanent Error (No Retry) ===")
    
    retry_handler = RetryHandler(initial_delay=1, max_attempts=3)
    
    def permanent_failure_func():
        print("Raising permanent error")
        raise PermanentError("TestService", "Authentication failed (401)")
    
    try:
        result = retry_handler.execute_with_retry(permanent_failure_func, "TestService")
        print("✗ Test failed - should have raised exception")
    except PermanentError as e:
        print(f"✓ Test passed - permanent error not retried: {e}")


def test_max_retries_exceeded():
    """Test max retries exceeded"""
    print("\n=== Test 4: Max Retries Exceeded ===")
    
    retry_handler = RetryHandler(initial_delay=1, max_attempts=3)
    
    def always_fail_func():
        print("Attempt failed")
        raise TransientError("TestService", "Service unavailable")
    
    try:
        result = retry_handler.execute_with_retry(always_fail_func, "TestService")
        print("✗ Test failed - should have raised exception")
    except TransientError as e:
        print(f"✓ Test passed - max retries exceeded: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("RETRY HANDLER STANDALONE TESTS")
    print("=" * 50)
    
    test_successful_call()
    test_transient_error_with_retry()
    test_permanent_error_no_retry()
    test_max_retries_exceeded()
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)
