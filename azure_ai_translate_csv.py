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
