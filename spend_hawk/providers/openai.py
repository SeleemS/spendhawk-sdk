"""OpenAI provider patching."""
import logging
from typing import Any
from functools import wraps

from ..utils import Timer
from .base import send_metric

logger = logging.getLogger(__name__)

_original_create = None
_original_async_create = None
_patched = False


def patch_openai():
    """Patch OpenAI API to intercept responses."""
    global _original_create, _original_async_create, _patched
    
    if _patched:
        logger.debug("OpenAI already patched")
        return
    
    try:
        import openai
        from openai import OpenAI
        from openai.resources.chat import completions
        
        # Patch sync create
        _original_create = completions.Completions.create
        completions.Completions.create = _patched_create
        
        logger.info("Successfully patched OpenAI")
        _patched = True
        
    except ImportError:
        logger.warning("OpenAI library not installed, skipping patch")
    except Exception as e:
        logger.error(f"Failed to patch OpenAI: {e}", exc_info=True)


def _patched_create(self, *args, **kwargs):
    """Patched version of OpenAI create method."""
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
                input_tokens = usage.prompt_tokens
                output_tokens = usage.completion_tokens
                
                # Send metric
                send_metric(
                    provider="openai",
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms
                )
        except Exception as e:
            logger.error(f"Error extracting OpenAI metrics: {e}", exc_info=True)
        
        return response
        
    except Exception as e:
        # If original call fails, still track the latency
        timer.stop()
        raise


def unpatch_openai():
    """Restore original OpenAI methods."""
    global _original_create, _patched
    
    if not _patched:
        return
    
    try:
        from openai.resources.chat import completions
        
        if _original_create:
            completions.Completions.create = _original_create
        
        _patched = False
        logger.info("OpenAI unpatched")
        
    except Exception as e:
        logger.error(f"Error unpatching OpenAI: {e}", exc_info=True)
