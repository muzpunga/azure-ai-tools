import os
import requests
import uuid
import json
from dotenv import load_dotenv
load_dotenv()


# Load key and endpoint from environment variables
key = os.getenv("AZURE_TRANSLATOR_KEY")
endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
location = os.getenv("AZURE_TRANSLATOR_LOCATION", "australiaeast")  # default can stay

if not key or not endpoint:
    raise ValueError("Missing environment variable: please set AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_ENDPOINT")

path = '/translate'
constructed_url = endpoint + path

# specify languages
params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['fr', 'zu']
}

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# simple text to be translated
body = [{
    'text': 'I would really like to drive your car around the block a few times!'
}]

response = requests.post(constructed_url, params=params, headers=headers, json=body)
print(json.dumps(response.json(), indent=4, ensure_ascii=False, sort_keys=True)) # print the translation
