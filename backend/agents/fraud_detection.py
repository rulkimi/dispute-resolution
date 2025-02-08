# agents/fraud_detection.py
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
from models import ChatMessage
from typing import List

load_dotenv()
PROJECT_ID = os.environ.get("PROJECT_ID")
vertexai.init(project=PROJECT_ID, location="us-central1")

class ChatFraudDetector:
    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-pro-002")

    def analyze_chat(self, messages: List[ChatMessage]) -> dict:
        """
        Analyzes a chat message for potential fraud, considering the history.

        Args:
            messages: A list of ChatMessage objects representing the conversation history.

        Returns:
            A dictionary containing:
            - is_fraudulent:  Boolean, True if fraud is detected.
            - reason: Textual explanation of the decision.
        """
        if not messages:
            return {"is_fraudulent": False, "reason": "No messages to analyze."}

        # Construct the prompt, including the conversation history.
        prompt = "Analyze the following chat conversation for potential fraud:\n\n"
        for msg in messages:
            prompt += f"Sender: {msg.sender_id}, Receiver: {msg.receiver_id}, Message: {msg.message}\n"

        prompt += "\nBased on this conversation, is there any indication of fraudulent activity? Explain your reasoning."

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.lower()

            if "yes" in text_response:  # Simple keyword check.  Improve in a real system.
                is_fraudulent = True
            else:
                is_fraudulent = False

            return {"is_fraudulent": is_fraudulent, "reason": response.text}

        except Exception as e:
            print(f"Error during fraud analysis: {e}")
            return {"is_fraudulent": False, "reason": f"AI analysis failed: {e}"}
