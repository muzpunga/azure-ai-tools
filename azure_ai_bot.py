"""
===============================================================================
Program:      azure_ai_bot.py
Description:  Starts a conversation with a Bot Framework bot using the Direct Line
              API, sends a message. Not yet trained.

Author:       Murray Pung
Date:         2025-06-03
Version:      1.0.0

Dependencies:
  - Python 3.6+
  - requests
  - python-dotenv

Environment Variables:
  - DIRECT_LINE_SECRET : Direct Line secret for authenticating with the bot service

Workflow:
  1. Start a conversation with the bot
  2. Send a text message ("Hello from Python!") to the bot
  3. Poll for and print any bot responses

Input:
  - No external files required

Output:
  - Prints conversation ID, sent message, and any bot replies to the console

Usage:
  - Ensure .env file contains DIRECT_LINE_SECRET
  - Run the script to interact with the bot via Direct Line API

Notes:
  - Includes a small delay to allow bot responses
  - The bot is not yet trained

Example:
  python direct_line_demo.py
===============================================================================
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get secret from environment variable
DIRECT_LINE_SECRET = os.getenv("DIRECT_LINE_SECRET")

if not DIRECT_LINE_SECRET:
    raise ValueError("Missing DIRECT_LINE_SECRET. Set it in your .env file.")

# 1. Start a conversation
headers = {
    "Authorization": f"Bearer {DIRECT_LINE_SECRET}"
}
response = requests.post("https://directline.botframework.com/v3/directline/conversations", headers=headers)
conversation = response.json()
conversation_id = conversation["conversationId"]
stream_url = conversation.get("streamUrl")

print("Conversation started. ID:", conversation_id)

# 2. Send a message to the bot
message_text = "Hello from Python!"
activity = {
    "type": "message",
    "from": {"id": "user1"},
    "text": message_text
}
requests.post(
    f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities",
    headers=headers,
    json=activity
)
print("Message sent:", message_text)

# 3. Poll for bot responses
time.sleep(2)  # Small delay to let the bot respond
response = requests.get(
    f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities",
    headers=headers
)
activities = response.json().get("activities", [])
for activity in activities:
    if activity["from"]["id"] != "user1":
        print("Bot replied:", activity["text"])

# the bot has not yet been trained
