from typing import Dict, Any, List
from fastapi import HTTPException
from models import ChatMessage, DisputeSubmission, Evidence
from agents.fraud_prevention import FraudDetector
from agents.dispute_resolution import DisputeResolver
from agents.fraud_detection import ChatFraudDetector
from db import save_chat_message, flag_conversation
import json
import asyncio


class DisputeOrchestrator:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.dispute_resolver = DisputeResolver()
        self.chat_fraud_detector = ChatFraudDetector()

    async def process_chat_message(self, message: ChatMessage) -> Dict[str, Any]:
        """
        Processes a regular chat message:
        - Checks for fraud patterns.
        - Checks for leaving intent.
        """
        is_suspicious, alerts = self.fraud_detector.analyze_message(message.message)
        if is_suspicious:
            await self._handle_fraud_alerts(message, alerts)
            return {
                "status": "blocked",
                "reason": "Suspicious activity detected",
                "alerts": alerts
            }

        # Check for leaving intent using AI analysis
        intent_result = await self.process_chat_intent(message)
        if intent_result.get("flagged"):
            return {"status": "warning", "reason": intent_result.get("reason")}
        
        return {"status": "clean"}

    async def process_chat_for_fraud(self, messages: List[dict]) -> Dict[str, Any]:
        """
        Processes a list of chat messages for fraud detection.
        """
        # Convert list of dicts to list of ChatMessage objects
        chat_messages = [ChatMessage(**msg) for msg in messages]
        analysis_result = self.chat_fraud_detector.analyze_chat(chat_messages)
        return analysis_result

    async def process_dispute(self, dispute: DisputeSubmission, evidence: Evidence = None) -> Dict[str, Any]:
        # First check for any historical fraud alerts
        fraud_history = await self.fraud_detector._check_fraud_history(dispute) # type: ignore
        if fraud_history["has_alerts"]:
            return {
                "status": "escalated",
                "reason": "Previous fraud alerts found",
                "requires_human_review": True
            }

        # Process the dispute resolution
        resolution = await self.dispute_resolver.resolve(dispute, evidence)
        
        if resolution["status"] == "approved":
            await self.dispute_resolver._release_funds(dispute) # type: ignore
        elif resolution["status"] == "escalated":
            await self.dispute_resolver._escalate_to_human(dispute, resolution["reason"]) # type: ignore
            
        return resolution

    async def process_chat_intent(self, message: ChatMessage) -> Dict[str, Any]:
        """
        Uses the AI model to analyze whether the chat message expresses an intent
        to leave the platform. Expected JSON output: {"intent": true/false}.
        """
        prompt = f"""
        You are a chat intent detection AI. Analyze the following chat message and determine if it indicates an intent
        to conduct the trade off-platform (e.g. settle privately, negotiate outside of the platform, etc.).

        Message: "{message.message}"

        Please output the result as a JSON string in the following format:
        {{"flagged": true, "reason": "Detailed explanation..."}} 
        or: {{"flagged": false}}.
        """
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, self.dispute_resolver.model.generate_content, prompt)
            result = json.loads(response.text)
            if result.get("intent"):
                await self._handle_leaving_intent(message)
                return {"flagged": True, "reason": "Leaving platform intent detected; system warnings have been sent."}
            return {"flagged": False}
        except Exception as e:
            return {"flagged": False, "reason": f"Intent analysis failed: {e}"}

    async def _handle_leaving_intent(self, message: ChatMessage):
        """
        Sends a system message warning both parties that leaving the platform is risky.
        Also flags the conversation for fraud review.
        """
        warning = (
            "WARNING: Leaving the platform is very risky. You will assume all liabilities, "
            "and the platform will not cover any losses. Please reconsider your action."
        )
        loop = asyncio.get_running_loop()

        # Create a system-generated message for the sender
        system_message_sender = {
            "sender_id": "system",
            "receiver_id": message.sender_id,
            "message": warning,
            "dispute_id": getattr(message, "dispute_id", None)
        }
        await loop.run_in_executor(None, save_chat_message, system_message_sender)

        # Create a system-generated message for the receiver
        system_message_receiver = {
            "sender_id": "system",
            "receiver_id": message.receiver_id,
            "message": warning,
            "dispute_id": getattr(message, "dispute_id", None)
        }
        await loop.run_in_executor(None, save_chat_message, system_message_receiver)

        # Flag the conversation in the database if a dispute_id is present
        dispute_id = getattr(message, "dispute_id", None)
        if dispute_id:
            await loop.run_in_executor(None, flag_conversation, dispute_id)

        # Log the action (could also update a UI flag)
        print("Conversation flagged for potential fraud (leaving intent detected).")

    async def process_dispute_chat_message(self, message: ChatMessage) -> Dict[str, Any]:
        """
        Processes messages exchanged during a dispute resolution chat.
        At this point, the conversation context is different – the buyer/seller are now interacting
        with an automated dispute resolution agent that can pull in historical trade context and profile data.
        """
        profile_info = self._get_profile_info(message.sender_id)
        context_message = f"User Profile: {profile_info}\nMessage: {message.message}"
        resolution = await self.dispute_resolver.resolve_from_chat(context_message)
        return resolution

    def _get_profile_info(self, user_id: str) -> str:
        return f"Profile data for user {user_id}"

    async def _handle_fraud_alerts(self, message: ChatMessage, alerts: List[str]):
        """
        Handles fraud alerts by printing/logging details.
        (This is also where you could update a flag in the database.)
        """
        alert_details = f"Fraud alert for message from {message.sender_id}: {'; '.join(alerts)}"
        print(alert_details)
        # Optionally: Update conversation flagged status in the database if required.
