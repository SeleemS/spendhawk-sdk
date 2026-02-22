"""Google Generative AI provider patching."""
import logging
from functools import wraps

from ..utils import Timer
from .base import send_metric

logger = logging.getLogger(__name__)

_original_generate_content = None
_patched = False


def patch_google():
    """Patch Google Generative AI API to intercept responses."""
    global _original_generate_content, _patched
    
    if _patched:
        logger.debug("Google Generative AI already patched")
        return
    
    try:
        from google.generativeai.generative_models import GenerativeModel
        
        # Patch generate_content method
        _original_generate_content = GenerativeModel.generate_content
        GenerativeModel.generate_content = _patched_generate_content
        
        logger.info("Successfully patched Google Generative AI")
        _patched = True
        
    except ImportError:
        logger.warning("Google Generative AI library not installed, skipping patch")
    except Exception as e:
        logger.error(f"Failed to patch Google Generative AI: {e}", exc_info=True)


def _patched_generate_content(self, *args, **kwargs):
    """Patched version of Google GenerativeModel.generate_content method."""
    timer = Timer()
    timer.start()
    
    try:
        # Call original method
        response = _original_generate_content(self, *args, **kwargs)
        
        # Extract metrics from response
        latency_ms = timer.stop()
        
        try:
            model = self.model_name
            
            # Extract token counts from usage_metadata
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count or 0
                output_tokens = usage.candidates_token_count or 0
                
                # Send metric
                send_metric(
                    provider="google",
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms
                )
            else:
                logger.debug("No usage_metadata found in Google Generative AI response")
        except Exception as e:
            logger.error(f"Error extracting Google Generative AI metrics: {e}", exc_info=True)
        
        return response
        
    except Exception as e:
        # If original call fails, still track the latency
        timer.stop()
        raise


def unpatch_google():
    """Restore original Google Generative AI methods."""
    global _original_generate_content, _patched
    
    if not _patched:
        return
    
    try:
        from google.generativeai.generative_models import GenerativeModel
        
        if _original_generate_content:
            GenerativeModel.generate_content = _original_generate_content
        
        _patched = False
        logger.info("Google Generative AI unpatched")
        
    except Exception as e:
        logger.error(f"Error unpatching Google Generative AI: {e}", exc_info=True)
