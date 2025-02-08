# models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class ChatMessage(BaseModel):
    sender_id: str
    receiver_id: str
    message: str

class DisputeType(str, Enum):
    BUYER_NOT_PAID = "buyer_not_paid"
    SELLER_NOT_RELEASED = "seller_not_released"
    BUYER_UNDERPAID = "buyer_underpaid"
    BUYER_OVERPAID = "buyer_overpaid"

class ProofType(str, Enum):
    VIDEO = "video"
    PDF = "pdf"

class Evidence(BaseModel):
    file_url: str
    file_type: ProofType
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    verification_status: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class DisputeSubmission(BaseModel):
    transaction_id: str
    dispute_type: DisputeType
    amount: float
    currency: str
    evidence: Optional[Evidence] = None
    additional_info: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
