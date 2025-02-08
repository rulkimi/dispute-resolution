from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException, Form
from models import DisputeSubmission, Evidence
from orchestrator import DisputeOrchestrator
from cloud_storage import upload_file_to_bucket
import os
from typing import Optional

router = APIRouter()

BUCKET_NAME = os.getenv("BUCKET_NAME", "deriv-dispute")

@router.post("/submit")
async def submit_dispute(dispute: DisputeSubmission, background_tasks: BackgroundTasks):
    # Save dispute details to db
    # db.save_dispute(dispute.dict())
    orchestrator = DisputeOrchestrator()
    background_tasks.add_task(orchestrator.process_dispute, dispute, dispute.evidence) # Pass evidence
    return {"status": "dispute submitted"}

@router.post("/upload-evidence")
async def upload_evidence(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    transaction_id: str = Form(...),
    # Add other fields as needed, matching your Evidence model
):
    """Uploads evidence and returns a file URL."""

    destination_blob_name = f"uploads/{transaction_id}/{file.filename}"
    try:
        gcs_uri = upload_file_to_bucket(file.file, BUCKET_NAME, destination_blob_name)

        # Create an Evidence object
        evidence = Evidence(
            file_url=gcs_uri,
            file_type=file_type,  # Ensure this matches your ProofType enum
            # upload_timestamp is automatically set by the model
        )
        return evidence  # Return the Evidence object

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    # Create a unique destination name, e.g., based on file.filename or a UUID
    destination_blob_name = f"uploads/videos/{file.filename}"
    try:
        # Upload and get the GCS URI
        gcs_uri = upload_file_to_bucket(file.file, BUCKET_NAME, destination_blob_name)
        return {"status": "success", "gcs_uri": gcs_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
