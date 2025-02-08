# chat.py
from fastapi import APIRouter, BackgroundTasks
from models import ChatMessage
from orchestrator import process_chat_message

router = APIRouter()

@router.post("/send")
async def send_chat(message: ChatMessage, background_tasks: BackgroundTasks):
    # Persist message to db (or log)
    # db.save_chat_message(message.dict())
    background_tasks.add_task(process_chat_message, message)
    return {"status": "message received"}
