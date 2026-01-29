import requests
from typing import Dict, Any
from exceptions.custom_exceptions import (
    TransientError, PermanentError, ServiceUnavailableError,
    AuthenticationError, InvalidPayloadError, QuotaExceededError,
    TimeoutError, NetworkError
)


class ExternalService:
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions"""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            raise ServiceUnavailableError(self.service_name, "Service temporarily unavailable", response)
        elif response.status_code in [408, 504]:
            raise TimeoutError(self.service_name, "Request timeout", response)
        elif response.status_code == 401:
            raise AuthenticationError(self.service_name, "Authentication failed", response)
        elif response.status_code == 400:
            raise InvalidPayloadError(self.service_name, "Invalid request payload", response)
        elif response.status_code == 429:
            raise QuotaExceededError(self.service_name, "Rate limit or quota exceeded", response)
        elif response.status_code >= 500:
            raise TransientError(self.service_name, f"Server error: {response.status_code}", response)
        else:
            raise PermanentError(self.service_name, f"Unexpected error: {response.status_code}", response)
    
    def handle_exception(self, exception: Exception):
        """Handle request exceptions"""
        if isinstance(exception, requests.exceptions.Timeout):
            raise TimeoutError(self.service_name, "Request timeout", exception)
        elif isinstance(exception, requests.exceptions.ConnectionError):
            raise NetworkError(self.service_name, "Network connection error", exception)
        elif isinstance(exception, requests.exceptions.RequestException):
            raise TransientError(self.service_name, "Request failed", exception)
        else:
            raise
