"""Utility functions for Spend Hawk SDK."""
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional


# Pricing data (per 1K tokens)
PRICING = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
    },
    "anthropic": {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
    }
}


def calculate_cost(
    provider: str, 
    model: str, 
    input_tokens: int, 
    output_tokens: int
) -> float:
    """
    Calculate cost for an API call.
    
    Args:
        provider: Provider name (openai, anthropic)
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Cost in USD
    """
    pricing = PRICING.get(provider, {}).get(model, {})
    if not pricing:
        return 0.0
    
    # Pricing is per 1K tokens
    input_cost = (input_tokens / 1000) * pricing.get("input", 0)
    output_cost = (output_tokens / 1000) * pricing.get("output", 0)
    
    return round(input_cost + output_cost, 6)


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
