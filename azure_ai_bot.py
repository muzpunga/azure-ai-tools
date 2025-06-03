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
