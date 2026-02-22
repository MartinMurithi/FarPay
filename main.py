from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
import uuid
import time

import models
import schemas
from database import engine, get_db


# Create the DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FarPay PaymentApi")


@app.get("/")
def health_check():
    """Confirms the server is running"""
    return {"statis": "active", "system": "FarPay"}


@app.post("/api/v1/payments/initiate", response_model=schemas.PaymentResponse)
def initiate_payment(payload: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """
    Receives payment details and saves them to DB
    It returns a PesaPal redirect URL
    """

    # Generate a tracking id
    transaction_ref = str(uuid.uuid4())

    # Create the DB record
    new_transaction = models.Transaction(
        amount=payload.amount,
        phone=payload.phone,
        transaction_ref=transaction_ref,
        transaction_status="PENDING",
    )

    # Save to DB
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # Generate the Redirect URL (Mocking the Pesapal call for now)
    # In a real scenario, this URL comes from the Pesapal API
    pesapal_url = f"https://cybqa.pesapal.com/sandbox/pay?id={transaction_ref}"

    return {
        "reference": transaction_ref,
        "redirect_url": pesapal_url,
        "status": new_transaction.status,  # Now this matches 'PENDING'
    }


@app.get("/api/v1/bank/mock")
def mock_bank_transfer():
    """Simulates the bank's internal processing delay."""

    time.sleep(3)  # Simulate network lag
    return {"message": "Funds verified by central bank", "code": 200}
