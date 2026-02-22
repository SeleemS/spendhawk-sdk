# Spend Hawk SDK

**Automatic LLM cost tracking for OpenAI and Anthropic.**

Track your AI API costs automatically with zero code changes. Spend Hawk intercepts API responses (never your API keys!) and sends usage metrics to your dashboard.

## Features

- 🔒 **Secure**: Never touches your API keys or request data
- ⚡ **Non-blocking**: < 1ms overhead, async background sends
- 🧵 **Thread-safe**: Works with multithreading and async code
- 📊 **Automatic**: No code changes needed after setup
- 💰 **Accurate**: Tracks tokens, latency, and calculates costs

## Installation

```bash
pip install spend-hawk-sdk
```

## Quick Start

```python
import spend_hawk
from openai import OpenAI

# 1. Initialize Spend Hawk (patches OpenAI and Anthropic)
spend_hawk.patch_all()

# 2. Optional: Set project context
spend_hawk.set_context(project_id="my-project", agent="my-agent")

# 3. Use OpenAI as normal - metrics auto-tracked!
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Metrics automatically sent to Spend Hawk backend 🎉
```

## Configuration

Set environment variables:

```bash
export SPEND_HAWK_API_KEY="your-api-key"
export SPEND_HAWK_API_ENDPOINT="https://api.spendhawk.com"  # optional
export SPEND_HAWK_PROJECT_ID="my-project"  # optional
export SPEND_HAWK_AGENT="my-agent"  # optional
```

Or configure in code:

```python
import spend_hawk

spend_hawk.config.api_key = "your-api-key"
spend_hawk.config.project_id = "my-project"
```

## Dynamic Context

Tag API calls dynamically:

```python
# Set context for all subsequent calls
spend_hawk.set_context(project_id="project-a", agent="agent-1")

# Use as context manager
with spend_hawk.context(project_id="project-b", agent="agent-2"):
    # API calls here will use this context
    response = client.chat.completions.create(...)

# Context restored after block
```

## Supported Providers

- ✅ OpenAI (GPT-4, GPT-3.5, etc.)
- ✅ Anthropic (Claude 3 Opus, Sonnet, Haiku)

## Security Model

**What we intercept:**
- Response metadata (model name, token counts, latency)

**What we NEVER see:**
- Your API keys
- Request prompts
- Response content

The SDK only reads response objects after your API call completes. All tracking happens locally before sending anonymized metrics.

## How It Works

1. `patch_all()` monkey-patches OpenAI and Anthropic clients
2. When you make an API call, the SDK:
   - Starts a timer
   - Calls the original API method
   - Extracts tokens and latency from the response
   - Calculates cost using current pricing
   - Sends metrics asynchronously (non-blocking)
   - Returns the original response unchanged

Total overhead: **< 1ms** per API call.

## Error Handling

Network failures or backend errors will **never crash your code**. All metric sending happens in a background thread with automatic retries.

```python
# Even if Spend Hawk backend is down, this works fine
response = client.chat.completions.create(...)  # ✅ Never crashes
```

## Testing

Run tests:

```bash
pip install pytest
pytest tests/
```

## Examples

### Basic usage

```python
import spend_hawk
spend_hawk.patch_all()

from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### With Anthropic

```python
import spend_hawk
spend_hawk.patch_all()

from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Multi-agent system

```python
import spend_hawk
spend_hawk.patch_all()

# Track different agents
with spend_hawk.context(agent="research-agent"):
    research_response = openai_call()

with spend_hawk.context(agent="writing-agent"):
    writing_response = openai_call()

# Dashboard shows costs per agent
```

## License

MIT

## Support

- Documentation: https://docs.spendhawk.com
- Issues: https://github.com/spend-hawk/spend-hawk-sdk/issues
- Email: support@spendhawk.com
