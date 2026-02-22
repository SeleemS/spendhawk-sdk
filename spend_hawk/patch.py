"""Main patching module."""
import logging

from .providers import patch_openai, patch_anthropic, patch_google, unpatch_openai, unpatch_anthropic, unpatch_google

logger = logging.getLogger(__name__)

_patched = False


def patch_all():
    """
    Patch all supported LLM providers.
    
    This will monkey-patch:
    - OpenAI (openai.ChatCompletion.create)
    - Anthropic (anthropic.Anthropic.messages.create)
    - Google Generative AI (google.generativeai.GenerativeModel.generate_content)
    
    The patches are non-blocking and will not crash your code if metrics
    fail to send.
    """
    global _patched
    
    if _patched:
        logger.debug("Already patched, skipping")
        return
    
    logger.info("Patching LLM providers...")
    
    # Patch each provider
    patch_openai()
    patch_anthropic()
    patch_google()
    
    _patched = True
    logger.info("All providers patched successfully")


def unpatch_all():
    """Restore all original provider methods."""
    global _patched
    
    if not _patched:
        return
    
    logger.info("Unpatching LLM providers...")
    
    unpatch_openai()
    unpatch_anthropic()
    unpatch_google()
    
    _patched = False
    logger.info("All providers unpatched")
