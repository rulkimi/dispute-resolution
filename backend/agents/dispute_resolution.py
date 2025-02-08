from models import DisputeSubmission, Evidence
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from dotenv import load_dotenv
import asyncio
import json
from db import get_split_chat_history  # Import the helper function

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID")
vertexai.init(project=PROJECT_ID, location="us-central1")

from video_analysis import analyze_video  # Import the video analysis function
from db import update_evidence_metadata  # Import the function to update evidence metadata

class DisputeResolver:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.0-flash-001")

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
            try:
                loop = asyncio.get_running_loop()
                video_result = await loop.run_in_executor(None, analyze_video, evidence.file_url)
                # Update evidence metadata with video analysis result if possible
                if hasattr(evidence, "id") and evidence.id is not None:
                    await loop.run_in_executor(None, update_evidence_metadata, evidence.id, {"analysis_result": video_result})
                else:
                    # If no id is available, update the metadata in-memory
                    evidence.metadata["analysis_result"] = video_result
            except Exception as e:
                video_result = f"Video analysis error: {e}"
            prompt += f"""
            Analyse this video evidence: {evidence.file_url} and extract important details like bank account information to help next steps in verification that the user made the right transfer to the right account.
            Analyse the behaviours and actions of the individual in the video to detect any suspicious activity.
            \n\nVideo Analysis Result:\n{video_result}"""
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

    async def resolve_from_chat(self, chat_context: str) -> dict:
        """
        Resolves a dispute chat message using AI analysis.
        Analyzes the chat context (which includes profile data and user message) and provides a resolution suggestion
        along with guidance on whether further evidence is needed.
        Returns a dictionary with:
          - status: e.g. "approved", "escalated", "evidence_requested"
          - reason: Explaining text
          - requires_human_review: Boolean flag indicating if escalation is necessary
        """
        prompt = f"""
        You are an AI dispute resolution assistant. Given the following context from a dispute chat conversation,
        analyze the conversation and provide a resolution suggestion along with guidance on next steps.
        
        Context:
        {chat_context}
        
        Please output your response as a JSON string in the following format:
        {{"status": "approved", "reason": "Concise explanation", "requires_human_review": false}}.
        """
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            result = json.loads(response.text)
            return result
        except Exception as e:
            return {"status": "escalated", "reason": f"AI resolution failed: {e}", "requires_human_review": True}

    async def finalize_resolution(self, dispute: DisputeSubmission, evidence: Evidence = None) -> dict:
        """
        Finalizes the dispute resolution workflow by integrating all available information.
        This method gathers:
          - Dispute details.
          - Pre-dispute and post-dispute chat histories fetched from the database.
          - Evidence metadata (if available).

        The AI model returns a final judgement in JSON format:
          {"status": "approved"/"rejected"/"escalated", "reason": "Explanation", "confidence": <number between 0 and 1>}
        
        If the confidence is below a predefined threshold, the dispute is escalated for human review.
        """
        # Retrieve chat history using the helper function
        pre_dispute_chat, post_dispute_chat = get_split_chat_history(dispute.id, dispute.created_at)
        
        prompt = f"""
        You are the final dispute resolution AI. Consolidate all available data to reach a final decision.

        Dispute Information:
        Transaction ID: {dispute.transaction_id}
        Dispute Type: {dispute.dispute_type}
        Amount: {dispute.amount} {dispute.currency}
        Additional Information: {dispute.additional_info or "None"}

        Pre-Dispute Chat History:
        {pre_dispute_chat}

        Post-Dispute Chat History:
        {post_dispute_chat}
        """
        if evidence:
            prompt += f"\nEvidence Metadata: {json.dumps(evidence.metadata)}"
        prompt += """
        Based on the above information, please provide your final judgement in the format:
        {"status": "approved", "reason": "Explanation", "confidence": <number between 0 and 1>}
        """
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            # Define the confidence threshold below which human review is required.
            CONFIDENCE_THRESHOLD = 0.8
            if result.get("confidence", 0) < CONFIDENCE_THRESHOLD:
                await self._escalate_to_human(dispute, "Final judgement confidence below threshold.")
                result["status"] = "escalated"
                result["requires_human_review"] = True
            else:
                if result.get("status") == "approved":
                    await self._release_funds(dispute)
            return result
        except Exception as e:
            return {"status": "escalated", "reason": f"Final resolution failed: {e}", "requires_human_review": True}

    async def _release_funds(self, dispute: DisputeSubmission):
        # Placeholder for fund release logic.  This would interact with a
        # payment gateway or internal accounting system.
        print(f"Funds released for transaction {dispute.transaction_id}")
        pass  # Replace with actual implementation

    async def _escalate_to_human(self, dispute: DisputeSubmission, reason: str):
        # Placeholder for escalating to a human agent.  This might involve
        # creating a ticket in a support system, sending a notification, etc.
        print(f"Dispute {dispute.transaction_id} escalated to human review. Reason: {reason}")
        pass  # Replace with actual implementation