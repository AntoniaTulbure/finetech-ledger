from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fintech Ledger API")

@app.post("/accounts/")
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(
        owner=account.owner,
        balance=account.initial_balance,
        currency=account.currency
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.get("/accounts/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.post("/transfer/")
def transfer_funds(request: schemas.TransferRequest, db: Session = Depends(get_db)):
    # Guardrail 1: Prevent transferring money to self
    if request.sender_id == request.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to the same account")

    # Guardrail 2: Prevent zero or negative transfers
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be greater than zero")

    sender = db.query(models.Account).filter(models.Account.id == request.sender_id).first()
    receiver = db.query(models.Account).filter(models.Account.id == request.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="One or both accounts not found")

    # Guardrail 3: Check for sufficient balance
    if sender.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    sender.balance -= request.amount
    receiver.balance += request.amount

    new_transaction = models.Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=request.amount
    )
    db.add(new_transaction)
    db.commit()

    return {"status": "success", "amount_transferred": request.amount}

# Feature: Get Transaction History for an Account
@app.get("/transactions/{account_id}", response_model=List[schemas.TransactionResponse])
def get_transaction_history(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    history = db.query(models.Transaction).filter(
        (models.Transaction.sender_id == account_id) | 
        (models.Transaction.receiver_id == account_id)
    ).all()
    
    return history