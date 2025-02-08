# chat.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from models import ChatMessage
from orchestrator import DisputeOrchestrator  # Import new function

router = APIRouter()

@router.post("/send")
async def send_chat(message: ChatMessage, background_tasks: BackgroundTasks):
    # Persist message to db (or log)
    # db.save_chat_message(message.dict())
    orchestrator = DisputeOrchestrator()
    background_tasks.add_task(orchestrator.process_chat_message, message)
    return {"status": "message received"}

from db import get_chat_history

@router.post("/webhook")  # New webhook endpoint
async def chat_webhook(message: ChatMessage, background_tasks: BackgroundTasks):
    try:
        # Get chat history
        history = get_chat_history()

        # Add current message to history
        history.append(message.model_dump())
        
        orchestrator = DisputeOrchestrator()
        background_tasks.add_task(orchestrator.process_chat_for_fraud, history)
        return {"status": "message received and processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
