# chat.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from models import ChatMessage
from orchestrator import DisputeOrchestrator
from db import save_chat_message, get_chat_history
import asyncio

router = APIRouter()

@router.post("/send")
async def send_chat(message: ChatMessage, background_tasks: BackgroundTasks):
    """
    Endpoint for p2p chat.
    Buyer and seller messages are persisted and then processed for fraud and intent analysis.
    """
    # Save the chat message to the database (wrapped in an executor)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, save_chat_message, message.dict())

    orchestrator = DisputeOrchestrator()
    # Process the chat message (fraud detection analysis)
    background_tasks.add_task(orchestrator.process_chat_message, message)
    return {"status": "message received"}

@router.post("/webhook")
async def chat_webhook(message: ChatMessage, background_tasks: BackgroundTasks):
    """
    Webhook endpoint that retrieves the full chat history,
    appends the current message, and then analyzes:
      - The complete conversation for fraudulent patterns,
      - And the intent of the latest message for any off‑platform indications.
    """
    loop = asyncio.get_running_loop()
    # Retrieve the full chat history (for all messages or optionally by dispute_id)
    history = await loop.run_in_executor(None, get_chat_history, None)
    # Append the current message to the conversation history
    history.append(message.dict())
    
    orchestrator = DisputeOrchestrator()
    background_tasks.add_task(orchestrator.process_chat_for_fraud, history)
    
    # Check for off‑platform intent using the AI-powered method.
    intent_result = await orchestrator.process_chat_intent(message)
    if intent_result.get("flagged", False):
        return {"status": "halted", "reason": intent_result.get("reason", "Off-platform intent detected")}
    return {"status": "message received and processed"}

@router.post("/intent-check")
async def check_chat_intent(message: ChatMessage):
    """
    An explicit endpoint to check the intent of a single message.
    """
    orchestrator = DisputeOrchestrator()
    result = await orchestrator.process_chat_intent(message)
    if result.get("flagged", False):
        return {"status": "halted", "reason": result.get("reason", "Off-platform intent detected")}
    return {"status": "ok"}

@router.post("/dispute/send")
async def send_dispute_chat(message: ChatMessage, dispute_id: str, background_tasks: BackgroundTasks):
    """
    Endpoint for exchanging messages during a dispute chat.
    In this context, messages might be persisted with an associated dispute_id
    (if applicable) and then processed by an automated dispute resolution agent.
    """
    # Optionally, append dispute_id to message dict and persist it.
    enriched_message = message.model_dump()
    enriched_message["dispute_id"] = dispute_id
    # Save the message using the DB helper
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, save_chat_message, enriched_message)
    orchestrator = DisputeOrchestrator()
    background_tasks.add_task(orchestrator.process_dispute_chat_message, message)
    # Optionally, you could persist dispute-related messages with a dispute_id:
    # loop = asyncio.get_running_loop()
    # await loop.run_in_executor(None, save_chat_message, {**message.dict(), "dispute_id": "<DISPUTE_ID>"})
    return {"status": "message received for dispute chat"}
