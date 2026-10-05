from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from datetime import datetime, timezone
from database import Base


class Account(Base):
    __tablename__="accounts"
    id= Column(Integer, primary_key=True, index=True)
    owner= Column(String, nullable=False)
    balance= Column(Numeric(precision=12, scale=2), nullable=False, default=0.00)
    currency= Column(String, default="USD")

class Transaction(Base):
    __tablename__="transactions"
    id=Column(Integer, primary_key=True, index=True)
    sender_id=Column(Integer, ForeignKey("accounts.id"), nullable=False)
    receiver_id=Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount=Column(Numeric(precision=12, scale=2), nullable=False)
    category=Column(String, default="Transfer")
    timestamp=Column(DateTime, default=lambda: datetime.now(timezone.utc))