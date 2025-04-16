# %%
import os

import anthropic
from dotenv import load_dotenv

from doc_tools import create_document

load_dotenv()


client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

PROMPT = "Generate a spooky story that is 1 paragraph long, and then upload it to Google docs."

TOOL_MAPPING = {
    "create_document": create_document,
    # "create_document": lambda title, text: print("Successfully created the document"),
}

TOOLS = [
        {
            "name": "create_document",
            "description": "Create a new Google Document with the given title and text",
            "input_schema": {
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
        },
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
# [TextBlock(citations=None, text="I'd be happy to create a spooky story for you and upload it to 
# Google Docs. Let me write a one-paragraph spooky story and then create the document for you.", type='text'), 
# ToolUseBlock(id='toolu_013aFg9xXVp4Z6m7htfEJwXJ', input={'title': 'Spooky Short Story', 
# 'text': 'The old mansion at the end of Willow Street ... and escape.'}, name='create_document', type='tool_use')]

# %%
create_doc_tool_request = [block for block in initial_response.content if block.type == "tool_use"][0]
create_doc_tool_reply = {
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": create_doc_tool_request.id,
            "content": str(TOOL_MAPPING[create_doc_tool_request.name](**create_doc_tool_request.input)),
        }
    ],
}

created_doc_response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=TOOLS,
    messages=[
        {"role": "user", "content": PROMPT},
        {"role": "assistant", "content": initial_response.content},
        create_doc_tool_reply
    ],
)

print(created_doc_response.content)

# Response
# [TextBlock(citations=None, text='I\'ve created a spooky story and uploaded it to 
# Google Docs with the title "Spooky Short Story." The document has been successfully 
# created and contains a one-paragraph spooky tale about Sarah\'s unsettling 
# experience at an abandoned mansion on Willow Street.', type='text')]
