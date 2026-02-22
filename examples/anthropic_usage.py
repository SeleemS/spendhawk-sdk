"""Anthropic usage example for Spend Hawk SDK."""
import os
import spend_hawk
from anthropic import Anthropic

# Set up environment variables
os.environ["SPEND_HAWK_API_KEY"] = "your-api-key-here"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key-here"

# Initialize Spend Hawk
spend_hawk.patch_all()
spend_hawk.set_context(project_id="my-project", agent="claude-agent")

# Use Anthropic as normal
client = Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.content[0].text)
print("\n✅ Metric automatically sent to Spend Hawk backend!")
