import time
import threading
from enum import Enum
from typing import Callable, Any
from exceptions.custom_exceptions import CircuitBreakerOpenError
from config.config import Config
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = Config.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        timeout: float = Config.CIRCUIT_BREAKER_TIMEOUT,
        half_open_attempts: int = Config.CIRCUIT_BREAKER_HALF_OPEN_ATTEMPTS
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts
        
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def get_state(self) -> CircuitState:
        with self.lock:
            self._check_timeout()
            return self.state
    
    def _check_timeout(self):
        """Check if timeout has passed and transition from OPEN to HALF_OPEN"""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            if time.time() - self.last_failure_time >= self.timeout:
                logger.info(f"{self.service_name}: Circuit breaker transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            self._check_timeout()
            
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    self.service_name,
                    f"Circuit breaker is OPEN for {self.service_name}"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_attempts:
                    logger.info(f"{self.service_name}: Circuit breaker transitioning to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(f"{self.service_name}: Circuit breaker transitioning to OPEN from HALF_OPEN")
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.failure_threshold:
                logger.warning(f"{self.service_name}: Circuit breaker OPENED after {self.failure_count} failures")
                self.state = CircuitState.OPEN
    
    def reset(self):
        """Manually reset circuit breaker"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            logger.info(f"{self.service_name}: Circuit breaker manually reset")
