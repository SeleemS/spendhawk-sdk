# MIT License - Copyright (c) 2026 Spend Hawk Contributors
# See LICENSE file for full license text
"""
Spend Hawk SDK - LLM Cost Tracking

Track your OpenAI and Anthropic API costs automatically with minimal overhead.

Usage:
    import spend_hawk
    
    # Initialize (patches OpenAI and Anthropic)
    spend_hawk.patch_all()
    
    # Set context (optional)
    spend_hawk.set_context(project_id="my-project", agent="my-agent")
    
    # Use OpenAI or Anthropic as normal
    import openai
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    # Metrics automatically sent to Spend Hawk backend
"""

__version__ = "0.1.0"

from .patch import patch_all, unpatch_all
from .context import set_context, get_context, context
from .config import config

__all__ = [
    'patch_all',
    'unpatch_all',
    'set_context',
    'get_context',
    'context',
    'config',
]
