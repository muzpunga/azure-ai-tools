"""
===============================================================================
Program:      azure_ai_translate.py
Description:  Translates a given English text into multiple target languages
              (French and Zulu) using Azure Cognitive Services Translator API.

Author:       Murray Pung
Date:         2025-06-03
Version:      1.0.0

Dependencies:
  - Python 3.6+
  - requests
  - python-dotenv

Environment Variables (in .env):
  - AZURE_TRANSLATOR_KEY       : Azure Translator subscription key
  - AZURE_TRANSLATOR_ENDPOINT  : Azure Translator endpoint URL
  - AZURE_TRANSLATOR_LOCATION  : Azure service region (default: australiaeast)

Workflow:
  1. Load Azure Translator credentials and region from environment variables
  2. Construct request URL and headers for the Translator Text API
  3. Define input text and target languages
  4. Send POST request to translate text
  5. Print JSON formatted translation results to console

Input:
  - Hardcoded English text in the script

Output:
  - JSON response printed to console showing translations

Usage:
  - Set Azure Translator credentials in .env file
  - Run script to see translated output

Notes:
  - Modify 'body' and 'params' to translate other text or add languages
  - Designed as a simple example of Translator Text API usage

Example:
  python azure_translator_sample.py
===============================================================================
"""

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
