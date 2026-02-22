"""Anthropic provider patching."""
import logging
from functools import wraps

from ..utils import Timer
from .base import send_metric

logger = logging.getLogger(__name__)

_original_create = None
_patched = False


def patch_anthropic():
    """Patch Anthropic API to intercept responses."""
    global _original_create, _patched
    
    if _patched:
        logger.debug("Anthropic already patched")
        return
    
    try:
        from anthropic.resources.messages import Messages
        
        # Patch create method
        _original_create = Messages.create
        Messages.create = _patched_create
        
        logger.info("Successfully patched Anthropic")
        _patched = True
        
    except ImportError:
        logger.warning("Anthropic library not installed, skipping patch")
    except Exception as e:
        logger.error(f"Failed to patch Anthropic: {e}", exc_info=True)


def _patched_create(self, *args, **kwargs):
    """Patched version of Anthropic create method."""
    timer = Timer()
    timer.start()
    
    try:
        # Call original method
        response = _original_create(self, *args, **kwargs)
        
        # Extract metrics from response
        latency_ms = timer.stop()
        
        try:
            model = response.model
            usage = response.usage
            
            if usage:
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens
                
                # Send metric
                send_metric(
                    provider="anthropic",
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms
                )
        except Exception as e:
            logger.error(f"Error extracting Anthropic metrics: {e}", exc_info=True)
        
        return response
        
    except Exception as e:
        # If original call fails, still track the latency
        timer.stop()
        raise


def unpatch_anthropic():
    """Restore original Anthropic methods."""
    global _original_create, _patched
    
    if not _patched:
        return
    
    try:
        from anthropic.resources.messages import Messages
        
        if _original_create:
            Messages.create = _original_create
        
        _patched = False
        logger.info("Anthropic unpatched")
        
    except Exception as e:
        logger.error(f"Error unpatching Anthropic: {e}", exc_info=True)
