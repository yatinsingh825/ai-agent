class ServiceException(Exception):
    """Base exception for all service errors"""
    def __init__(self, service_name, message, original_exception=None):
        self.service_name = service_name
        self.message = message
        self.original_exception = original_exception
        super().__init__(f"[{service_name}] {message}")


class TransientError(ServiceException):
    """Errors that can be retried (timeouts, 503, network issues)"""
    pass


class PermanentError(ServiceException):
    """Errors that should not be retried (401, 400, quota exceeded)"""
    pass


class TimeoutError(TransientError):
    """Request timeout errors"""
    pass


class NetworkError(TransientError):
    """Network connectivity errors"""
    pass


class ServiceUnavailableError(TransientError):
    """503 Service Unavailable errors"""
    pass


class AuthenticationError(PermanentError):
    """401 Authentication errors"""
    pass


class InvalidPayloadError(PermanentError):
    """400 Bad Request / Invalid payload errors"""
    pass


class QuotaExceededError(PermanentError):
    """429 Rate limit / quota exceeded errors"""
    pass


class CircuitBreakerOpenError(ServiceException):
    """Circuit breaker is open, failing fast"""
    pass
