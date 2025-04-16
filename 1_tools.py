
# %%
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

PROMPT = (
    "find 201122 removed from 316043 and then find the square root of the result. "
    "Return this value **only** with no other words."
)


# This time, we give the LLM some tools it can use as it's finding the answer
def subtract(a: int, b: int) -> int:
    return a-b

def sqrt(num: int) -> float:
    return num**0.5

TOOL_MAPPING = {
    "subtract": subtract,
    "sqrt": sqrt,
}

TOOLS = [
        {
            "name": "subtract",
            "description": "Calculate the difference between `a` and `b`",
            "input_schema": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "The first operand",
                    },
                    "b": {
                        "type": "number",
                        "description": "The second operand; the number to be subracted",
                    }
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "sqrt",
            "description": "Find the square root of an integer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "num": {
                        "type": "number",
                        "description": "The operand to find the square root of",
                    },
                },
                "required": ["num"],
            },
        }
    ]

# %%
initial_response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=TOOLS,
    messages=[{"role": "user", "content": PROMPT}],
)

print(initial_response.content)

# Response
# [TextBlock(citations=None, text="I need to find the difference between 316043 and 201122, and then calculate the square root of that result. I'll use the appropriate tools to do this.", type='text'), 
# ToolUseBlock(id='toolu_01Vq1MnteDMJVEcJoLpTqupe', input={'a': 316043, 'b': 201122}, name='subtract', type='tool_use')]

# %%
subract_tool_request = [block for block in initial_response.content if block.type == "tool_use"][0]
subract_tool_reply = {
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": subract_tool_request.id,
            "content": str(TOOL_MAPPING[subract_tool_request.name](**subract_tool_request.input)),
        }
    ],
}

intermediate_response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=TOOLS,
    messages=[
        {"role": "user", "content": PROMPT},
        {"role": "assistant", "content": initial_response.content},
        subract_tool_reply
    ],
)

print(intermediate_response.content)

# Response
# [TextBlock(citations=None, text="Now I'll find the square root of this result:", type='text'), 
# ToolUseBlock(id='toolu_01PtfMubJWYJtZ9KNDqQ7Zn1', input={'num': 114921}, name='sqrt', type='tool_use')]

# %%
sqrt_tool_request = [block for block in intermediate_response.content if block.type == "tool_use"][0]
sqrt_tool_reply = {
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": sqrt_tool_request.id,
            "content": str(TOOL_MAPPING[sqrt_tool_request.name](**sqrt_tool_request.input)),
        }
    ],
}

final_response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=TOOLS,
    messages=[
        {"role": "user", "content": PROMPT},
        {"role": "assistant", "content": initial_response.content},
        subract_tool_reply,
        {"role": "assistant", "content": intermediate_response.content},
        sqrt_tool_reply,
    ],
)

print(final_response.content)

# Response
# [TextBlock(citations=None, text='339.0', type='text')]
# %%
