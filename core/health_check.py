import time
import threading
import logging
from typing import Dict, Callable
from config.config import Config

logger = logging.getLogger(__name__)


class HealthCheckManager:
    def __init__(self, check_interval: float = Config.HEALTH_CHECK_INTERVAL):
        self.check_interval = check_interval
        self.services: Dict[str, Callable] = {}
        self.service_health: Dict[str, bool] = {}
        self.running = False
        self.thread = None
    
    def register_service(self, service_name: str, health_check_func: Callable):
        """Register a service with its health check function"""
        self.services[service_name] = health_check_func
        self.service_health[service_name] = False
        logger.info(f"Registered health check for {service_name}")
    
    def start(self):
        """Start periodic health checks"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.thread.start()
        logger.info("Health check manager started")
    
    def stop(self):
        """Stop health checks"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Health check manager stopped")
    
    def _health_check_loop(self):
        """Continuous health check loop"""
        while self.running:
            for service_name, health_check_func in self.services.items():
                try:
                    is_healthy = health_check_func()
                    previous_health = self.service_health.get(service_name, False)
                    self.service_health[service_name] = is_healthy
                    
                    if is_healthy and not previous_health:
                        logger.info(f"{service_name}: Service recovered and is now HEALTHY")
                    elif not is_healthy and previous_health:
                        logger.warning(f"{service_name}: Service became UNHEALTHY")
                
                except Exception as e:
                    logger.error(f"{service_name}: Health check failed with error: {e}")
                    self.service_health[service_name] = False
            
            time.sleep(self.check_interval)
    
    def is_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        return self.service_health.get(service_name, False)
    
    def get_all_health_status(self) -> Dict[str, bool]:
        """Get health status of all services"""
        return self.service_health.copy()
