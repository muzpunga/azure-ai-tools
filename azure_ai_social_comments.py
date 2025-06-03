"""
===============================================================================
Program:      azure_ai_social_comments.py
Description:  Designed to perform sentiment analysis of social media comments.
              Reads text files from an input directory, performs document-level
              sentiment analysis using Azure Cognitive Services Text Analytics,
              and writes sentiment results to an output directory.

Author:       Murray Pung
Date:         2025-06-03
Version:      1.0.0

Dependencies:
  - Python 3.6+
  - azure-ai-textanalytics
  - azure-core
  - python-dotenv

Environment Variables:
  - AZURE_TEXTANALYTICS_ENDPOINT : Your Azure Text Analytics service endpoint
  - AZURE_TEXTANALYTICS_KEY      : Your Azure Text Analytics subscription key

Input:
  - Text files (*.txt) located in 'data/comments/input'

Output:
  - Sentiment analysis results saved as text files in 'data/comments/output'

Usage:
  - Ensure .env file contains the required environment variables
  - Run the script to analyze all input text files automatically

Notes:
  - Skips empty files
  - Summarizes sentiment with overall mood description
  - Output filenames replace 'comment_' prefix with 'sentiment_'

Example:
  python sentiment_analysis.py
===============================================================================
"""

import os
import glob
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# configure
endpoint = os.getenv("AZURE_TEXTANALYTICS_ENDPOINT")
key = os.getenv("AZURE_TEXTANALYTICS_KEY")

input_dir = "data/comments/input"
output_dir = "data/comments/output"
input_pattern = os.path.join(input_dir, "*.txt")

client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

os.makedirs(output_dir, exist_ok=True)

# extract .txt files
input_files = glob.glob(input_pattern)

if not input_files:
    raise FileNotFoundError(f"No .txt files found in {input_dir}")

for filepath in input_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        full_text = f.read().strip()

    if not full_text:
        print(f"Skipping {filepath}: file is empty.")
        continue

    print(f"Processing {filepath} as a single document...")

    # perform sentiment analysis
    response = client.analyze_sentiment(documents=[full_text])[0]

    if response.is_error:
        output_content = f"Error processing {os.path.basename(filepath)}:\n{response.error.message}\n"
    else:
        sentiment = response.sentiment
        scores = response.confidence_scores
        output_content = (
            f"File: {os.path.basename(filepath)}\n"
            f"Overall Sentiment: {sentiment}\n"
            f"Scores:\n"
            f"  Positive: {scores.positive:.2f}\n"
            f"  Neutral : {scores.neutral:.2f}\n"
            f"  Negative: {scores.negative:.2f}\n"
        )

        # summarise
        if sentiment == 'positive':
            mood = "The overall mood is optimistic and favorable."
        elif sentiment == 'negative':
            mood = "The overall mood is critical or unfavorable."
        else:
            mood = "The overall mood is neutral or mixed."

        output_content += f"\nSummary: {mood}\n"

    # output
    filename = os.path.basename(filepath).replace("comment_", "sentiment_")
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(output_content)

    print(f"✔ Output written to {output_path}")
