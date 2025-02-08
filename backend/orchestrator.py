# orchestrator.py
from typing import Dict, Any
from fastapi import HTTPException
from models import ChatMessage, DisputeSubmission, Evidence
from agents.fraud_prevention import FraudDetector
from agents.dispute_resolution import DisputeResolver

class DisputeOrchestrator:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.dispute_resolver = DisputeResolver()

    async def process_chat_message(self, message: ChatMessage) -> Dict[str, Any]:
        is_suspicious, alerts = self.fraud_detector.analyze_message(message.message)
        
        if is_suspicious:
            await self._handle_fraud_alerts(message, alerts)
            return {
                "status": "blocked",
                "reason": "Suspicious activity detected",
                "alerts": alerts
            }
        
        return {"status": "clean"}

    async def process_dispute(self, dispute: DisputeSubmission, evidence: Evidence = None) -> Dict[str, Any]:
        # First check for any historical fraud alerts
        fraud_history = await self._check_fraud_history(dispute)
        if fraud_history["has_alerts"]:
            return {
                "status": "escalated",
                "reason": "Previous fraud alerts found",
                "requires_human_review": True
            }

        # Process the dispute resolution
        resolution = await self.dispute_resolver.resolve(dispute, evidence)
        
        if resolution["status"] == "approved":
            await self._release_funds(dispute)
        elif resolution["status"] == "escalated":
            await self._escalate_to_human(dispute, resolution["reason"])
            
        return resolution
