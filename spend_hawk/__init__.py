# MIT License - Copyright (c) 2026 Spend Hawk Contributors
# See LICENSE file for full license text
"""
Spend Hawk SDK - LLM Cost Tracking

Track your OpenAI, Anthropic, and Google Generative AI costs automatically with minimal overhead.

Usage:
    import spend_hawk
    
    # Initialize (patches OpenAI, Anthropic, and Google)
    spend_hawk.patch_all()
    
    # Set context (optional)
    spend_hawk.set_context(project_id="my-project", agent="my-agent")
    
    # Use OpenAI, Anthropic, or Google as normal
    import openai
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    # Metrics automatically sent to Spend Hawk backend
"""

__version__ = "0.1.2"

from .patch import patch_all, unpatch_all
from .context import set_context, get_context, context
from .config import config
from .pricing import init_pricing, get_pricing, calculate_cost, refresh_pricing

__all__ = [
    'patch_all',
    'unpatch_all',
    'set_context',
    'get_context',
    'context',
    'config',
    'init_pricing',
    'get_pricing',
    'calculate_cost',
    'refresh_pricing',
]
