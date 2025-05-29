# %% this is a simple LLM call
import os

import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# We give this calculation to the LLM, where the true answer is 339
PROMPT = (
    "find 201122 removed from 316043 and then find the square root of the result. "
    "Return this value **only** with no other words."
)

# %%
response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=1024,
    messages=[{"role": "user", "content": PROMPT}],
)

print(response.choices[0].message.content)

# CLAUDE ANSWER: 114.9195780204327 (you may get something different)
# Even worse, if you repeat the question, you can get a different answer

# %%
