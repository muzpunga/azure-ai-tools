"""
===============================================================================
Program:      azure_ai_speech.py
Description:  Transcribes all WAV audio files in the 'audio' folder into
              multiple specified languages using Azure Cognitive Services
              Speech SDK. Saves transcription text files to 'transcriptions'
              folder.

Author:       Murray Pung
Date:         2025-06-03
Version:      1.0.0

Dependencies:
  - Python 3.6+
  - azure-cognitiveservices-speech
  - python-dotenv

Environment Variables (in .env):
  - AZURE_SPEECH_KEY      : Azure Speech service subscription key
  - AZURE_SPEECH_REGION   : Azure Speech service region

Workflow:
  1. Load Azure Speech credentials from environment
  2. For each WAV file in 'audio' folder, transcribe audio to multiple
     languages (currently English and Portuguese)
  3. Save transcriptions as text files in 'transcriptions' folder,
     with language suffix in filename
  4. Provide console output for progress and errors

Input:
  - WAV audio files in 'audio' folder

Output:
  - Transcription text files in 'transcriptions' folder
    (filename format: original_name.{language}.txt)

Usage:
  - Set Azure credentials in .env
  - Place WAV files in 'audio'
  - Run the script

Notes:
  - Supports multiple languages by specifying language codes in the script
  - Handles recognition failures and no-match cases with appropriate messages

Example:
  python azure_speech_transcription.py
===============================================================================
"""

import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

if not speech_key or not service_region:
    raise ValueError("Missing Azure Speech credentials. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env.")

# Folders
audio_folder = "audio" # input audio is stored in this folder
transcriptions_folder = "transcriptions" # the output transcriptions are placed in this folder

# Create folder if it doesn't exist
os.makedirs(transcriptions_folder, exist_ok=True)

# specify the languages
languages = {
    "en-US": "english",
    "pt-BR": "portuguese"
}

# Transcribe all .wav files in the folder
for file_name in os.listdir(audio_folder):
    if file_name.lower().endswith(".wav"):
        wav_path = os.path.join(audio_folder, file_name)
        print(f"🎧 Processing {file_name}")

        for lang_code, lang_name in languages.items():
            print(f"🗣️ Transcribing to {lang_name}...")

            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.speech_recognition_language = lang_code
            audio_config = speechsdk.AudioConfig(filename=wav_path)
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            result = recognizer.recognize_once()

            # output
            lang_suffix = f".{lang_name}.txt"
            output_file = os.path.join(transcriptions_folder, file_name.replace(".wav", lang_suffix))

            with open(output_file, "w") as f:
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    f.write(result.text)
                    print(f"Saved: {output_file}")
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    f.write("[No speech could be recognized]")
                    print(f"No match for {lang_name}: {file_name}")
                else:
                    f.write("[Speech recognition failed]")
                    print(f"Failed for {lang_name}: {file_name} — {result.reason}")
