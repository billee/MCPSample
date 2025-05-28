# %%
import os

import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
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
        "type": "function",
        "function": {
            "name": "subtract",
            "description": "Calculate the difference between `a` and `b`",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sqrt",
            "description": "Find the square root of an integer",
            "parameters": {
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
    }
]

# %%
initial_response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=1024,
    tools=TOOLS,
    messages=[{"role": "user", "content": PROMPT}],
)

print('Initial response:')
print(initial_response)
print(initial_response.choices[0].message)

# %%
if initial_response.choices[0].message.tool_calls:
    tool_call = initial_response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = eval(tool_call.function.arguments)
    
    tool_result = TOOL_MAPPING[tool_name](**tool_args)
    
    tool_reply = {
        "role": "user",
        "content": None,
        "tool_call_id": tool_call.id,
        "name": tool_name,
        "tool_calls": [tool_call]
    }
    
    intermediate_response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": PROMPT},
            {"role": "assistant", "content": None, "tool_calls": [tool_call]},
            {"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": str(tool_result)}
        ],
    )
    
    print('Intermediate response:')
    print(intermediate_response)
    print(intermediate_response.choices[0].message)
    
    if intermediate_response.choices[0].message.tool_calls:
        tool_call = intermediate_response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = eval(tool_call.function.arguments)
        
        tool_result = TOOL_MAPPING[tool_name](**tool_args)
        
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            tools=TOOLS,
            messages=[
                {"role": "user", "content": PROMPT},
                {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                {"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": str(tool_result)}
            ],
        )
        
        print('Final response:')
        print(final_response)
        print(final_response.choices[0].message)
        print(final_response.choices[0].message.content)

# %%
