# dispute.py
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from models import DisputeSubmission, Evidence
from orchestrator import process_dispute
from cloud_storage import upload_file_to_bucket
import os

router = APIRouter()

BUCKET_NAME = os.getenv("BUCKET_NAME", "deriv-dispute")

@router.post("/submit")
async def submit_dispute(dispute: DisputeSubmission, background_tasks: BackgroundTasks):
    # Save dispute details to db
    # db.save_dispute(dispute.dict())
    background_tasks.add_task(process_dispute, dispute)
    return {"status": "dispute submitted"}

@router.post("/upload-evidence")
async def upload_evidence(evidence: Evidence):
    # Process file storage and associate with a dispute
    return {"status": "evidence received"}

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