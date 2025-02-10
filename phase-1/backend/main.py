import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

def configure_model():
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  return genai.GenerativeModel(
    model_name="gemini-2.0-flash-001",
    generation_config={"response_mime_type": "application/json"},
  )

def build_prompt():
    return """Analyze the following text and determine if the user is attempting to leave the platform.  Look for phrases suggesting a switch to another communication channel, even subtle indications or indirect suggestions. Consider slang, informal language, and Gen Z slang. Pay close attention to any expression of inconvenience with the current platform or preference for another.

Examples of phrases indicating a platform switch intent:

* "Let's continue on WhatsApp"
* "Do you have Insta?"
* "We can talk on Telegram"
* "Let's move to Messenger"
* "Switch to Signal"
* "Continue on WeChat"
* "Talk on Viber"
* "Hit me up on WhatsApp"
* "My Insta is..."
* "Text me on Telegram"
* "DM me on Messenger"
* "Let's chat on Signal"
* "Add me on WeChat"
* "My Viber is..."
* "WhatsApp me!"
* "Let's use Insta instead"
* "I'm on Telegram now"
* "Slide into my DMs on Insta"
* "Hit me up on my WhatsApp"
* "My Snapchat is..."
* "Let's chat on Snap"
* "What's your Insta?"
* "Let's connect on TikTok"
* "My TikTok is..."
* "I'm bouta head to Insta"
* "Bet, hmu on WhatsApp"
* "Let's take this convo to Insta"
* "This platform is kinda slow"
* "I prefer chatting on WhatsApp"
* "Is there a way to continue this on Telegram?"
* "WhatsApp is easier for me"
* "I find this platform less convenient"
* "Let's chat on WhatsApp Business"
* "My number is..."
* "Call me on..."
* "Let's connect on Facebook"
* "Check my Instagram"
* "My Telegram is..."
* "Let's use Telegram instead"
* "I'm on Imo now"
* "Let's chat on Imo"
* "My Imo is..."
* "Let's use 2go"
* "My 2go is..."


Return a JSON object with a "platform_switch_intent" field (boolean, true if a switch is indicated, false otherwise) and a "text" field containing the original text.
"""

@app.post("/analyze_text")
async def analyze_text(text: str):
  try:
    model = configure_model()
    prompt = build_prompt() + f"Text to analyze: {text}"

    print(f"Analyzing text...")
    response = model.generate_content([prompt])

    if not response:
      raise Exception("Failed to generate response from the AI model.")
  
    return {
      "status": "success", 
      "message": "Success", 
      "data": json.loads(response.text)
    }
  
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail={"status": "error", "message": str(e), "data": None},
    )
