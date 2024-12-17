import json
import requests
import os
from openai import OpenAI
from assistant_instructions import assistant_instructions
from dotenv import load_dotenv, dotenv_values


load_dotenv()

# Init OpenAI Client
client = OpenAI()

# Add lead to Airtable
def create_lead(name="", company_name="", phone="", email=""):
    url = "https://api.airtable.com/v0/appxw9Xs3duyir4Lq/Leads"
    headers = {
        "Authorization" : 'Bearer ' + dotenv_values().get("AIRTABLE_API_KEY"),
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Name": name,
                "Phone": phone,
                "Email": email,
                "CompanyName": company_name,
            }
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Lead created successfully.")
        return response.json()
    else:
        print(f"Failed to create lead: {response.text}")


def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # If there is an assistant.json file already, then load that assistant
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # If no assistant.json is present, create a new assistant using the below specifications

        file = client.files.create(file=open("knowledge.docx", "rb"), purpose='assistants')









        # Create the assistant
        assistant = client.beta.assistants.create(
            name="FimakAI",
            instructions=assistant_instructions,
            model="gpt-4o-mini",
            tools=[
                {
                    "type": "file_search"  # This adds the knowledge base as a tool
                },
                {
                    "type": "function",  # This adds the lead capture as a tool
                    "function": {
                        "name": "create_lead",
                        "description": "Capture lead details and save to Airtable.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the lead."
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "Phone number of the lead."
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Email of the lead."
                                },
                                "company_name": {
                                    "type": "string",
                                    "description": "CompanyName of the lead."
                                }
                            },
                            "required": ["name", "email", "company_name"]
                        }
                    }
                }
            ],
            tool_resources={
                "file_search":
                {
                    "vector_stores": [{"file_ids":[file.id]}]
                }
            }
        )

        # Save assistant details to a json file
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id


