import asyncio
from db import save_dispute, get_chat_history, save_chat_message
from models import DisputeSubmission

class DisputeManager:
    """
    A centralized manager for dispute lifecycle management.
    It creates disputes, retrieves dispute details and conversation history, and saves dispute chat messages.
    """
    async def create_dispute(self, dispute_data: dict):
        """
        Creates a new dispute record in the database.
        """
        loop = asyncio.get_running_loop()
        dispute = await loop.run_in_executor(None, save_dispute, dispute_data)
        return dispute

    async def save_dispute_chat_message(self, message_data: dict):
        """
        Saves a dispute-related chat message using a provided dispute ID.
        """
        loop = asyncio.get_running_loop()
        saved_msg = await loop.run_in_executor(None, save_chat_message, message_data)
        return saved_msg

    async def get_dispute_conversation(self, dispute_id: str):
        """
        Retrieves the chat conversation for a specific dispute.
        This can be filtered by dispute_id.
        """
        loop = asyncio.get_running_loop()
        history = await loop.run_in_executor(None, get_chat_history, dispute_id)
        return history

    # You can add further methods such as updating dispute status or linking evidence if needed. 