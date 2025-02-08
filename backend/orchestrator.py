from typing import Dict, Any, List
from fastapi import HTTPException
from models import ChatMessage, DisputeSubmission, Evidence
from agents.fraud_prevention import FraudDetector
from agents.dispute_resolution import DisputeResolver
from agents.fraud_detection import ChatFraudDetector


class DisputeOrchestrator:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.dispute_resolver = DisputeResolver()
        self.chat_fraud_detector = ChatFraudDetector()

    async def process_chat_message(self, message: ChatMessage) -> Dict[str, Any]:
        is_suspicious, alerts = self.fraud_detector.analyze_message(message.message)

        if is_suspicious:
            await self._handle_fraud_alerts(message, alerts)  # type: ignore
            return {
                "status": "blocked",
                "reason": "Suspicious activity detected",
                "alerts": alerts
            }

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
