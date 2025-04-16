import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]

def create_document(title: str="Placeholder", text: str="Placeholder") -> str:
    """Creates a new document with title 'example' and text 'made with API'."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)

        # Create a new document
        document = {
            'title': title
        }
        doc = service.documents().create(body=document).execute()
        print(f'Created document with title: {doc.get("title")}')
        
        # Get the document ID
        document_id = doc.get('documentId')
        
        # Add the text body to the document
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': text
                }
            }
        ]
        
        service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}).execute()
        
        print(f'Added text to the document. Document ID: {document_id}')
        return "Succesfully created the document."
        
    except HttpError as err:
        print(err)
        return f"An error occurred: {err}"


if __name__ == "__main__":
    create_document("Made with API", "This document was created and modified using the Google Docs API.")