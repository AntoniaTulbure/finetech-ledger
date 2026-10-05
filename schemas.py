from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class AccountCreate(BaseModel):
    owner: str
    initial_balance: Decimal
    currency: str = "USD"

class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: Decimal

class TransactionResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    amount: Decimal
    category: str
    timestamp: datetime

    class Config:
        from_attributes = True