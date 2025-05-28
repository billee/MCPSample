# %%
import os

import openai
from dotenv import load_dotenv

from doc_tools import create_document

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

PROMPT = "Generate a spooky story that is 1 paragraph long, and then upload it to Google docs."

TOOL_MAPPING = {
    "create_document": create_document,
    # "create_document": lambda title, text: print("Successfully created the document"),
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_document",
            "description": "Create a new Google Document with the given title and text",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the document",
                    },
                    "text": {
                        "type": "string",
                        "description": "The text to insert into the document body",
                    }
                },
                "required": ["title", "text"],
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

if initial_response.choices[0].message.tool_calls:
    tool_call = initial_response.choices[0].message.tool_calls[0]
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
    print(final_response.choices[0].message.content)
