"""Utility functions for Spend Hawk SDK."""
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Import calculate_cost from pricing module
from .pricing import calculate_cost as _calculate_cost


def calculate_cost(
    provider: str, 
    model: str, 
    input_tokens: int, 
    output_tokens: int
) -> float:
    """
    Calculate cost for an API call.
    
    Args:
        provider: Provider name (openai, anthropic, google) - ignored, uses model name directly
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Cost in USD
    """
    # Use dynamic pricing module (provider parameter kept for backward compatibility)
    return _calculate_cost(model, input_tokens, output_tokens)


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


class Timer:
    """Simple timer for measuring latency."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
    
    def stop(self) -> int:
        """
        Stop the timer and return elapsed time in milliseconds.
        
        Returns:
            Elapsed time in milliseconds
        """
        self.end_time = time.time()
        if self.start_time is None:
            return 0
        return int((self.end_time - self.start_time) * 1000)
