from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import DisputeSubmissionDB, SessionLocal, get_split_chat_history, update_evidence_metadata
# from models import DisputeSubmission  # Correct model name (not DisputeSubmissionDB)
from agents.dispute_resolution import DisputeResolver
from video_analysis import analyze_video
import asyncio
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_context: str
    message: str

class FinalizeDisputeRequest(BaseModel):
    additional_info: str  # Example of additional input

# This dependency matches the one defined in db.py,
# ensuring the session is correctly created and closed.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{dispute_id}/finalize", response_model=dict)
async def finalize_dispute(dispute_id: str, payload: FinalizeDisputeRequest, db: Session = Depends(get_db)):
    """
    Finalizes a dispute resolution by retrieving dispute details, associated evidence,
    and splitting chat history into pre and post dispute segments. Then, it calls the
    finalize_resolution function to generate the final AI resolution. This final summary
    is formatted as JSON for easy consumption by frontend UI for human review.
    """
    # Retrieve the dispute record by its ID. This includes associated evidence if it exists.
    dispute = db.query(DisputeSubmissionDB).filter(DisputeSubmissionDB.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Evidence is optionally retrieved via the relationship in the dispute record.
    evidence = dispute.evidence

    # If evidence exists and is of type VIDEO, analyze the video.
    if evidence and evidence.file_type == "video":
        loop = asyncio.get_running_loop()
        try:
            video_description = await loop.run_in_executor(None, analyze_video, evidence.file_url)
            # Update the evidence metadata with the video description.
            updated_evidence = await loop.run_in_executor(None, update_evidence_metadata, evidence.id, {"video_description": video_description})

            if updated_evidence:
                evidence = updated_evidence # Use updated evidence
        except Exception as e:
            print(f"Error analyzing video: {e}")
            #  Handle the error appropriately, e.g., log it and continue.


    # Retrieve the split chat history (pre- and post-dispute) using the dispute's creation timestamp.
    pre_chat, post_chat = get_split_chat_history(dispute_id, dispute.created_at)

    # Instantiate the dispute resolution AI agent.
    dispute_resolver = DisputeResolver()

    # Use the additional input from the payload
    additional_info = payload.additional_info

    # Finalize the resolution using the AI agent.
    final_result = await dispute_resolver.finalize_resolution(dispute, evidence=evidence)

    # Prepare evidence metadata for the summary.
    evidence_metadata = evidence.evidence_metadata if evidence else None

    # Aggregate all relevant details into a summary for the frontend.
    summary = {
        "dispute_details": {
            "transaction_id": dispute.transaction_id,
            "dispute_type": dispute.dispute_type,
            "amount": dispute.amount,
            "currency": dispute.currency,
            "additional_info": additional_info,
            "created_at": str(dispute.created_at)
        },
        "chat_history": {
            "pre_dispute": pre_chat,
            "post_dispute": post_chat
        },
        "evidence_metadata": evidence_metadata,
        "final_resolution": {
            "status": final_result.get("status"),
            "reason": final_result.get("reason"),
            "confidence": final_result.get("confidence"),
            "requires_human_review": final_result.get("requires_human_review", False)
        }
    }

    return summary

@router.post("/{dispute_id}/chat", response_model=dict)
async def interactive_dispute_chat(dispute_id: str, payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint for interactive dispute chat.
    Expects a JSON payload with:
      - "conversation_context": String representing the conversation so far.
      - "message": The new message sent by the user.
    Returns the AI-generated response which includes guidance, suggestions, and any evidence request.
    """
    try:
        dispute_id_int = int(dispute_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid dispute id.")

    dispute = db.query(DisputeSubmissionDB).filter(DisputeSubmissionDB.id == dispute_id_int).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    conversation_context = payload.conversation_context
    new_message = payload.message
    
    if not new_message:
        raise HTTPException(status_code=400, detail="Message must be provided.")
    
    dispute_resolver = DisputeResolver()
    result = await dispute_resolver.interactive_chat(dispute, conversation_context, new_message)
    
    return result
