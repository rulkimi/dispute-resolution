from models import DisputeSubmission, Evidence
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID")
vertexai.init(project=PROJECT_ID, location="us-central1")

class DisputeResolver:
    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-pro-002")

    async def resolve(self, dispute: DisputeSubmission, evidence: Evidence = None) -> dict:
        """
        Resolves a dispute using AI analysis.

        Args:
            dispute: The dispute submission details.
            evidence: Optional evidence provided.

        Returns:
            A dictionary representing the resolution.  Includes:
            - status:  "approved", "rejected", or "escalated"
            - reason:  A textual explanation of the decision.
            - confidence: (Optional) A score from 0 to 1 indicating confidence.
            - requires_human_review: (Optional) Boolean flag.
        """

        prompt = f"""
        You are a dispute resolution expert for a P2P platform.  Analyze the following dispute and provide a resolution:

        Transaction ID: {dispute.transaction_id}
        Dispute Type: {dispute.dispute_type}
        Amount: {dispute.amount} {dispute.currency}
        Additional Information: {dispute.additional_info or 'No additional information provided.'}
        """
        if evidence and evidence.file_type == "video":
            prompt += f"""
            Analyse this video evidence: {evidence.file_url} and extract important details like bank account information to help next steps in verification that the user made the right transfer to the right account.
            Analyse the behaviours and actions of the individual in the video to detect any suspicious activity.
            """
        elif evidence and evidence.file_type == "pdf":
            prompt += f"""
            Analyse this pdf evidence: {evidence.file_url} and extract important details like bank account information to help next steps in verification that the user made the right transfer to the right account.
            """

        prompt += """
        Based on this information, determine whether the dispute should be:

        - Approved (in favor of the submitter)
        - Rejected (in favor of the other party)
        - Escalated (requires human review)

        Provide a concise reason for your decision.
        """

        try:
            response = self.model.generate_content(prompt)
            # In a real application, you would parse the response more carefully,
            # potentially using a structured output format (e.g., JSON) from the LLM.
            # Here, we'll do a simple text-based parsing.
            text_response = response.text.lower()

            if "approved" in text_response:
                status = "approved"
            elif "rejected" in text_response:
                status = "rejected"
            else:
                status = "escalated"

            return {
                "status": status,
                "reason": response.text,  # Full text for now
                "requires_human_review": status == "escalated"
            }

        except Exception as e:
            print(f"Error during dispute resolution: {e}")
            return {
                "status": "escalated",
                "reason": f"AI resolution failed: {e}",
                "requires_human_review": True
            }

    async def _release_funds(self, dispute):
        # Placeholder for fund release logic.  This would interact with a
        # payment gateway or internal accounting system.
        print(f"Funds released for transaction {dispute.transaction_id}")
        pass  # Replace with actual implementation

    async def _escalate_to_human(self, dispute, reason):
        # Placeholder for escalating to a human agent.  This might involve
        # creating a ticket in a support system, sending a notification, etc.
        print(f"Dispute {dispute.transaction_id} escalated to human review. Reason: {reason}")
        pass  # Replace with actual implementation