# db.py (simplified)
chats = []
disputes = []

def save_chat_message(message: dict):
    chats.append(message)

def save_dispute(dispute: dict):
    disputes.append(dispute)
