"""
===============================================================================
Program:      azure_ai_translate_csv.py
Description:  Reads English texts from a CSV file, translates each text into 
              Brazilian Portuguese using Azure Cognitive Services Translator API,
              and saves the translated results back to a new CSV file.

Author:       Murray Pung
Date:         2025-06-03
Version:      1.0.0

Dependencies:
  - Python 3.6+
  - requests
  - pandas
  - python-dotenv

Environment Variables (in .env):
  - AZURE_TRANSLATOR_CSV_KEY       : Azure Translator subscription key
  - AZURE_TRANSLATOR_CSV_ENDPOINT  : Azure Translator endpoint URL
  - AZURE_TRANSLATOR_CSV_REGION    : Azure service region

Workflow:
  1. Load Azure Translator CSV credentials from environment variables
  2. Load English texts from input CSV (column named 'text')
  3. For each text, send request to Azure Translator API to translate into pt-BR
  4. Append translated text as a new column 'Portuguese_BR' to the DataFrame
  5. Save the DataFrame with translations into an output CSV file
  6. Adds a small delay between API calls to avoid throttling

Input:
  - CSV file: data/interesting_text.csv with column 'text'

Output:
  - CSV file: data/translated_to_portuguese_br.csv including 'Portuguese_BR' column

Usage:
  - Ensure input CSV exists and credentials are set in .env
  - Run script to generate translated CSV

Notes:
  - Adjust languages and filenames as needed
  - Handles API response errors gracefully by inserting None for failed translations

Example:
  python azure_translator_csv.py
===============================================================================
"""

import requests
import uuid
import pandas as pd
import time
import os
from dotenv import load_dotenv

# load credentials from .env
load_dotenv()

translator_key_csv = os.getenv("AZURE_TRANSLATOR_CSV_KEY")
translator_endpoint_csv = os.getenv("AZURE_TRANSLATOR_CSV_ENDPOINT")
translator_region_csv = os.getenv("AZURE_TRANSLATOR_CSV_REGION")

if not translator_key_csv or not translator_endpoint_csv or not translator_region_csv:
    raise ValueError("Missing Azure Translator CSV credentials in environment variables.")

# endpoint and parameters
path = '/translate'
constructed_url = translator_endpoint_csv + path

# specify languages
params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['pt-BR']  # Brazilian Portuguese
}

headers = {
    'Ocp-Apim-Subscription-Key': translator_key_csv,
    'Ocp-Apim-Subscription-Region': translator_region_csv,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# file paths
input_csv_file = os.path.join('data', 'interesting_text.csv')
output_csv_file = os.path.join('data', 'translated_to_portuguese_br.csv')

# load input
df = pd.read_csv(input_csv_file)
texts = df['text'].tolist()
translations_pt = []

# translate each text
for text in texts:
    body = [{'text': text}]
    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    result = response.json()

    try:
        pt_text = result[0]['translations'][0]['text']
    except (IndexError, KeyError, TypeError):
        pt_text = None

    translations_pt.append(pt_text)
    time.sleep(0.1)  # add a delay to avoid API throttling

# write translation
df['Portuguese_BR'] = translations_pt
df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')


print(f"Translations saved to {output_csv_file}")
