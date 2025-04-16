# %%
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

# We give this calculation to the LLM, where the true answer is 339
PROMPT = (
    "find 201122 removed from 316043 and then find the square root of the result. "
    "Return this value **only** with no other words."
)


# %%
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[{"role": "user", "content": PROMPT}],
)

print(response.content) # [TextBlock(citations=None, text='385', type='text')]

# CLAUDE ANSWER: 114.9195780204327 (you may get something different)
# Even worse, if you repeat the question, you can get a different answer

# %%
