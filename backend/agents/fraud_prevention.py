from typing import Tuple, List
from models import ChatMessage

class FraudDetector:
    def __init__(self):
        # Initialize any necessary resources, e.g., load a pre-trained model or rules.
        # For this prototype, we'll use a simple keyword-based approach.
        self.suspicious_keywords = ["urgent", "guarantee", "free money", "password", "bank details"]

    def analyze_message(self, message_text: str) -> Tuple[bool, List[str]]:
        """
        Analyzes a chat message for suspicious content.

        Args:
            message_text: The text of the chat message.

        Returns:
            A tuple: (is_suspicious, alerts).
            is_suspicious: True if the message is deemed suspicious, False otherwise.
            alerts: A list of strings describing the detected suspicious patterns.
        """
        alerts = []
        is_suspicious = False
        message_text_lower = message_text.lower()

        for keyword in self.suspicious_keywords:
            if keyword in message_text_lower:
                alerts.append(f"Suspicious keyword detected: '{keyword}'")
                is_suspicious = True

        return is_suspicious, alerts

    async def _check_fraud_history(self, dispute):
        # Placeholder for checking historical fraud data.  In a real system,
        # this would query a database of past user behavior, transactions, and
        # any previous fraud reports.
        # For now, we'll simulate a simple check.
        if "user123" in [dispute.buyer_id, dispute.seller_id]:  # Example: Check if user123 is involved
            return {"has_alerts": True, "details": ["Previous report for phishing."]}
        return {"has_alerts": False}