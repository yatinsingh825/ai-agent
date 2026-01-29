import json
import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileLogger:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
    
    def log_event(
        self,
        service_name: str,
        error_category: str,
        retry_count: int,
        circuit_breaker_state: str,
        message: str,
        additional_data: Dict[str, Any] = None
    ):
        """Log event to file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service_name": service_name,
            "error_category": error_category,
            "retry_count": retry_count,
            "circuit_breaker_state": circuit_breaker_state,
            "message": message
        }
        
        if additional_data:
            log_entry.update(additional_data)
        
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.debug(f"Logged event to file: {service_name}")
        
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
