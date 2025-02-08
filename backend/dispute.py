from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException, Form
from models import DisputeSubmission, Evidence
from orchestrator import DisputeOrchestrator
from cloud_storage import upload_file_to_bucket
from dispute_manager import DisputeManager
from db import save_evidence
import os
from typing import Optional
import asyncio

router = APIRouter()

BUCKET_NAME = os.getenv("BUCKET_NAME", "deriv-dispute")
dispute_manager = DisputeManager()

@router.post("/submit")
async def submit_dispute(dispute: DisputeSubmission, background_tasks: BackgroundTasks):
    """
    Endpoint to submit a dispute.
    The dispute details are saved to the database via the DisputeManager
    and then processed.
    """
    dispute_record = await dispute_manager.create_dispute(dispute.dict())
    
    orchestrator = DisputeOrchestrator()
    # Process the dispute in the background (AI analysis, verification, etc.)
    background_tasks.add_task(orchestrator.process_dispute, dispute, dispute.evidence)
    return {"status": "dispute submitted", "dispute_id": dispute_record.id}

@router.post("/upload-evidence")
async def upload_evidence(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    transaction_id: str = Form(...)
):
    """
    Uploads evidence and returns an Evidence object.
    On success, stores the evidence details to the database.
    """
    destination_blob_name = f"uploads/{transaction_id}/{file.filename}"
    try:
        gcs_uri = upload_file_to_bucket(file.file, BUCKET_NAME, destination_blob_name)
        evidence_obj = Evidence(
            file_url=gcs_uri,
            file_type=file_type  # Ensure this matches your ProofType enum
        )
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, save_evidence, evidence_obj.dict())
        return evidence_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Uploads a video file and returns the corresponding GCS URI.
    """
    destination_blob_name = f"uploads/videos/{file.filename}"
    try:
        gcs_uri = upload_file_to_bucket(file.file, BUCKET_NAME, destination_blob_name)
        return {"status": "success", "gcs_uri": gcs_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
