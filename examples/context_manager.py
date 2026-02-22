"""Context manager usage example for Spend Hawk SDK."""
import os
import spend_hawk
from openai import OpenAI

os.environ["SPEND_HAWK_API_KEY"] = "your-api-key-here"
os.environ["OPENAI_API_KEY"] = "your-openai-key-here"

spend_hawk.patch_all()

client = OpenAI()

# Use context manager for temporary context
print("Agent 1 doing research...")
with spend_hawk.context(project_id="multi-agent", agent="research-agent"):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Research AI trends"}]
    )
    print(f"Research: {response.choices[0].message.content[:50]}...")

print("\nAgent 2 doing writing...")
with spend_hawk.context(project_id="multi-agent", agent="writing-agent"):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Write a blog post"}]
    )
    print(f"Writing: {response.choices[0].message.content[:50]}...")

print("\n✅ Dashboard will show costs per agent!")
