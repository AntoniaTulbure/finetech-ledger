from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from pydantic import BaseModel, Field

import models
from database import engine, get_db

# Create the database tables in ledger.db automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fintech Ledger API")

# Request model for transferring money
class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: Decimal = Field(gt=0, decimal_places=2)

# Request model for creating an account
class AccountCreate(BaseModel):
    owner: str
    initial_balance: Decimal = Field(gt=0, decimal_places=2)
    currency: str = "USD"

@app.get("/")
def home():
    return {"message": "Welcome to the Fintech Ledger API!"}

# Endpoint to create a new account
@app.post("/accounts/")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(
        owner=account.owner,
        balance=account.initial_balance,
        currency=account.currency
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

# Endpoint to fetch an account by ID
@app.get("/accounts/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# Endpoint to transfer funds safely between two accounts
@app.post("/transfer/")
def transfer_funds(req: TransferRequest, db: Session = Depends(get_db)):
    sender = db.query(models.Account).filter(models.Account.id == req.sender_id).first()
    receiver = db.query(models.Account).filter(models.Account.id == req.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver account not found")

    if sender.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Perform atomic transfer
    sender.balance -= req.amount
    receiver.balance += req.amount

    # Record the transaction
    new_transaction = models.Transaction(
        sender_id=req.sender_id,
        receiver_id=req.receiver_id,
        amount=req.amount
    )
    db.add(new_transaction)

    # Save all changes to the database
    db.commit()

    return {"status": "success", "amount_transferred": str(req.amount)}