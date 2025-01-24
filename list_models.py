import requests
import os
import json

api_key = os.environ.get("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"

headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

response = requests.get(url, headers=headers)

for model in response.json().get("data"):
    print(model.get("id"))

# writing the response to a file of the key "id"
with open("response.json", "w") as file:
    json.dump(response.json(), file, indent=4)
