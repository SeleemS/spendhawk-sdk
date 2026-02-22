"""HTTP client for sending metrics to Spend Hawk backend."""
import logging
import time
from typing import Dict, Any, Optional
import threading
from queue import Queue
import requests

from .config import config

logger = logging.getLogger(__name__)


class MetricsClient:
    """Client for sending metrics to Spend Hawk backend."""
    
    def __init__(self):
        self.queue: Queue = Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        
    def start_worker(self):
        """Start background worker thread for sending metrics."""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
    
    def _worker(self):
        """Background worker that processes the metrics queue."""
        while self.running:
            try:
                # Get metric from queue (with timeout to allow checking running flag)
                try:
                    metric = self.queue.get(timeout=1.0)
                except:
                    continue
                
                # Send metric with retries
                self._send_with_retry(metric)
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in metrics worker: {e}", exc_info=True)
    
    def _send_with_retry(self, metric: Dict[str, Any], max_retries: int = 3):
        """
        Send metric with exponential backoff retry logic.
        
        Args:
            metric: Metric data to send
            max_retries: Maximum number of retry attempts
        """
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{config.api_endpoint}/api/v1/metrics",
                    json=metric,
                    headers={
                        "Authorization": f"Bearer {config.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=5.0
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    logger.debug(f"Successfully sent metric: {metric}")
                    return
                elif response.status_code == 401:
                    logger.error("Invalid Spend Hawk API key")
                    return  # Don't retry auth errors
                else:
                    logger.warning(
                        f"Failed to send metric (attempt {attempt + 1}/{max_retries}): "
                        f"HTTP {response.status_code}"
                    )
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout sending metric (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Network error sending metric (attempt {attempt + 1}/{max_retries}): {e}"
                )
            except Exception as e:
                logger.error(f"Unexpected error sending metric: {e}", exc_info=True)
                return  # Don't retry unexpected errors
            
            # Exponential backoff (0.5s, 1s, 2s)
            if attempt < max_retries - 1:
                time.sleep(0.5 * (2 ** attempt))
        
        logger.error(f"Failed to send metric after {max_retries} attempts")
    
    def send_async(self, metric: Dict[str, Any]):
        """
        Send metric asynchronously (non-blocking).
        
        Args:
            metric: Metric data to send
        """
        if not config.is_configured():
            logger.debug("Spend Hawk not configured, skipping metric")
            return
        
        # Start worker if not running
        self.start_worker()
        
        # Add to queue
        self.queue.put(metric)
    
    def shutdown(self):
        """Shutdown the worker thread gracefully."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)


# Global client instance
client = MetricsClient()
