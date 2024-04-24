import json
import requests
import os
from openai import OpenAI

# Assuming assistant_instructions is defined in a module named prompts
from prompts import assistant_instructions  

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MAKE_COM_WEBHOOK_URL = os.environ['MAKE_COM_WEBHOOK_URL']

# Initialize OpenAI Client with v2 API settings
client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"})

# Send user data along with a message explaining the contact reason to a webhook on make.com
def send_to_webhook(name, email, message):
    url = MAKE_COM_WEBHOOK_URL  # The webhook URL
    data = {"name": name, "email": email, "message": message}
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Data sent successfully to webhook.")
        return response.json()
    else:
        print(f"Failed to send data: {response.text}")

# Create or load an assistant
def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # Load the existing assistant if the file exists
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Create a new assistant if no existing data is found
        # Uploading a document to associate with the assistant
        file = client.files.create(file=open("knowledge.pdf", "rb"), purpose='assistants')

        # Creating a new assistant with the specified instructions, model, and tools
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-4-turbo",
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [file.id]}}
        )

        # Save the new assistant ID in a JSON file for future use
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
