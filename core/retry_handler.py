import time
import logging
from typing import Callable, Any
from exceptions.custom_exceptions import TransientError, PermanentError
from config.config import Config

logger = logging.getLogger(__name__)


class RetryHandler:
    def __init__(
        self,
        initial_delay: float = Config.RETRY_INITIAL_DELAY,
        max_attempts: int = Config.RETRY_MAX_ATTEMPTS,
        backoff_multiplier: float = Config.RETRY_BACKOFF_MULTIPLIER
    ):
        self.initial_delay = initial_delay
        self.max_attempts = max_attempts
        self.backoff_multiplier = backoff_multiplier
    
    def execute_with_retry(
        self,
        func: Callable,
        service_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with exponential backoff retry logic.
        Only retries on TransientError.
        """
        attempt = 0
        delay = self.initial_delay
        
        while attempt < self.max_attempts:
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"{service_name}: Succeeded after {attempt} retries")
                return result
            
            except PermanentError as e:
                logger.error(f"{service_name}: Permanent error - not retrying: {e}")
                raise
            
            except TransientError as e:
                attempt += 1
                if attempt >= self.max_attempts:
                    logger.error(f"{service_name}: Max retries ({self.max_attempts}) exceeded")
                    raise
                
                logger.warning(
                    f"{service_name}: Transient error (attempt {attempt}/{self.max_attempts}). "
                    f"Retrying in {delay}s... Error: {e}"
                )
                time.sleep(delay)
                delay *= self.backoff_multiplier
            
            except Exception as e:
                logger.error(f"{service_name}: Unexpected error: {e}")
                raise
        
        raise TransientError(service_name, "Max retries exceeded")
