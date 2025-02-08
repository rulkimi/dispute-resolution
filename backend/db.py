from typing import List, Dict

# In-memory chat history
_chat_history: List[Dict] = []

def get_chat_history() -> List[Dict]:
    """Retrieves the chat history."""
    return _chat_history

def save_chat_message(message: Dict):
    """Saves a chat message to the history."""
    _chat_history.append(message)
