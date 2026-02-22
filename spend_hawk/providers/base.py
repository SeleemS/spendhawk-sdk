"""Base patching logic shared across providers."""
import logging
from typing import Dict, Any, Optional

from ..client import client
from ..context import get_context
from ..config import config
from ..utils import calculate_cost, get_timestamp

logger = logging.getLogger(__name__)


def send_metric(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    **extra_fields
):
    """
    Send metric to backend asynchronously.
    
    Args:
        provider: Provider name (openai, anthropic)
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        latency_ms: Latency in milliseconds
        **extra_fields: Additional fields to include
    """
    try:
        # Get context
        ctx = get_context()
        
        # Calculate cost
        cost = calculate_cost(provider, model, input_tokens, output_tokens)
        
        # Build metric payload
        metric = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "latency_ms": latency_ms,
            "timestamp": get_timestamp(),
            "project_id": ctx.get('project_id') or config.project_id,
            "agent": ctx.get('agent') or config.agent,
            **extra_fields
        }
        
        # Send asynchronously
        client.send_async(metric)
        
    except Exception as e:
        # Never crash user code
        logger.error(f"Error sending metric: {e}", exc_info=True)
