import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Use the DATABASE_URL environment variable if provided, otherwise default to a local SQLite DB
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database model for chat messages. A column "dispute_id" has been added to
# optionally bind messages to a dispute conversation.
# The "flagged" column indicates if the conversation has been flagged for potential fraud or risky behavior.
class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, index=True)
    receiver_id = Column(String, index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dispute_id = Column(String, nullable=True)
    flagged = Column(Boolean, default=False)

# Database model for dispute submissions. Evidence is stored as a one-to-one relationship.
class DisputeSubmissionDB(Base):
    __tablename__ = "disputes"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    buyer_id = Column(String, index=True)
    seller_id = Column(String, index=True)
    dispute_type = Column(String)
    amount = Column(Float)
    currency = Column(String)
    additional_info = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    evidence = relationship("EvidenceDB", back_populates="dispute", uselist=False)

# Database model for evidence provided in a dispute.
class EvidenceDB(Base):
    __tablename__ = "evidences"
    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String)
    file_type = Column(String)
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    verification_status = Column(String, nullable=True)
    evidence_metadata = Column(JSON, default={})
    dispute_id = Column(Integer, ForeignKey("disputes.id"))
    dispute = relationship("DisputeSubmissionDB", back_populates="evidence")

# Call this to create tables automatically on app start-up
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI routes if needed
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to save a chat message to the database.
def save_chat_message(message_data: dict):
    db = SessionLocal()
    chat_message = ChatMessageDB(**message_data)
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    db.close()
    return chat_message

# Helper function to get a chat history.
# If a dispute_id is provided, only messages linked to that dispute are returned.
def get_chat_history(dispute_id: str = None):
    db = SessionLocal()
    if dispute_id:
        messages = db.query(ChatMessageDB).filter(ChatMessageDB.dispute_id == dispute_id).all()
    else:
        messages = db.query(ChatMessageDB).all()
    db.close()
    return messages

# Helper function to save a dispute submission.
def save_dispute(dispute_data: dict):
    db = SessionLocal()
    dispute = DisputeSubmissionDB(**dispute_data)
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    db.close()
    return dispute

# Helper function to save evidence.
def save_evidence(evidence_data: dict):
    db = SessionLocal()
    evidence = EvidenceDB(**evidence_data)
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    db.close()
    return evidence

def update_evidence_metadata(evidence_id: int, metadata: dict):
    db = SessionLocal()
    evidence = db.query(EvidenceDB).filter(EvidenceDB.id == evidence_id).first()
    if evidence:
        current_metadata = evidence.evidence_metadata or {}
        current_metadata.update(metadata)
        evidence.evidence_metadata = current_metadata #Correct field
        db.commit()
        db.refresh(evidence)
    db.close()
    return evidence

def flag_conversation(dispute_id: str):
    """
    Updates all chat messages for a given dispute to flagged = True.
    """
    db = SessionLocal()
    try:
        db.query(ChatMessageDB).filter(ChatMessageDB.dispute_id == dispute_id).update({"flagged": True})
        db.commit()
    finally:
        db.close()

def get_split_chat_history(dispute_id: str, dispute_created_at):
    """
    Retrieve all chat messages for the given dispute_id and split them into two groups:
    - pre_chat: messages with created_at before the dispute_created_at timestamp.
    - post_chat: messages with created_at on or after the dispute_created_at timestamp.
    
    Each message is formatted as "sender_id: message (at created_at)".
    """
    db = SessionLocal()
    messages = db.query(ChatMessageDB).filter(ChatMessageDB.dispute_id == dispute_id).order_by(ChatMessageDB.created_at.asc()).all()
    db.close()

    pre_chat = []
    post_chat = []
    for msg in messages:
        formatted_msg = f"{msg.sender_id}: {msg.message} (at {msg.created_at})"
        if msg.created_at < dispute_created_at:
            pre_chat.append(formatted_msg)
        else:
            post_chat.append(formatted_msg)
    return "\n".join(pre_chat), "\n".join(post_chat)
