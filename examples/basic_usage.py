"""Basic usage example for Spend Hawk SDK."""
import os
import spend_hawk
from openai import OpenAI

# Set up environment variables
os.environ["SPEND_HAWK_API_KEY"] = "your-api-key-here"
os.environ["OPENAI_API_KEY"] = "your-openai-key-here"

# Initialize Spend Hawk (patches OpenAI and Anthropic)
spend_hawk.patch_all()

# Optional: Set project context
spend_hawk.set_context(project_id="my-project", agent="example-agent")

# Use OpenAI as normal - metrics are automatically tracked!
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
print("\n✅ Metric automatically sent to Spend Hawk backend!")
