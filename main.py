from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import uuid
import time

import models
import schemas
from database import engine, get_db


# Create the DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FarPay PaymentApi")

print("========================================")
print("   FARSIGHT DEMO: WAITING FOR REQUESTS  ")
print("========================================")


@app.get("/")
def health_check():
    """Confirms the server is running"""
    return {"statis": "active", "system": "FarPay"}


@app.get("/api/v1/bank/mock")
def mock_bank_transfer():
    """Simulates the bank's internal processing delay."""

    time.sleep(3)  # Simulate network lag
    return {"message": "Funds verified by central bank", "code": 200}


@app.get("/api/v1/payments/callback")
def pesapal_callback(
    OrderTrackingId: str, OrderMerchantReference: str, db: Session = Depends(get_db)
):
    """
    This is the IPN endpoint Pesapal calls after a user pays.
    """
    # Find the transaction in our DB
    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_ref == OrderMerchantReference)
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.transaction_status = "COMPLETED"

    db.commit()

    return {
        "status": "OK",
        "message": f"Transaction {OrderMerchantReference} updated to COMPLETED",
    }


@app.get("/api/v1/payments/history", response_model=list[schemas.TransactionRecord])
def get_all_transactions(db: Session = Depends(get_db)):
    """
    Returns a list of all payments in the database.
    This will be used by the Android app's 'History' screen.
    """
    transactions = db.query(models.Transaction).all()
    return transactions


from services import (
    get_pesapal_token,
    get_transaction_status,
    register_ipn,
    submit_order,
)


@app.get("/api/v1/test-auth")
def test_pesapal_auth():
    token = get_pesapal_token()
    if token:
        return {"status": "Success", "token_preview": f"{token[:15]}..."}
    return {"status": "Failed", "message": "Check your console for errors"}


@app.get("/api/v1/register-ipn")
def setup_ipn(ngrok_url: str):
    token = get_pesapal_token()
    if not token:
        return {"error": "Could not get token"}

    result = register_ipn(token, ngrok_url)
    return result


@app.post("/api/v1/payments/initiate", response_model=schemas.PaymentResponse)
def initiate_payment(payload: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """
    1. Saves the pending transaction to your database.
    2. Calls Pesapal V3 to get a real payment link.
    3. Updates the DB with the Pesapal Tracking ID.
    """

    merchant_ref = str(uuid.uuid4())[:12]

    new_transaction = models.Transaction(
        amount=payload.amount,
        phone=payload.phone,
        transaction_ref=merchant_ref,
        transaction_status="PENDING",
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    token = get_pesapal_token()

    order_data = {
        "amount": payload.amount,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "phone": payload.phone,
        "merchant_reference": merchant_ref,
    }

    result = submit_order(token, order_data)

    if result and result.get("status") == "200":

        pesapal_tracking_id = result.get("order_tracking_id")

        new_transaction.pesapal_tracking_id = pesapal_tracking_id
        db.commit()

        return {
            "reference": merchant_ref,
            "redirect_url": result.get("redirect_url"),
            "status": "PENDING",
        }

    new_transaction.transaction_status = "FAILED"
    db.commit()
    raise HTTPException(status_code=500, detail="Pesapal could not process the request")


@app.get("/api/v1/payments/callback")
def payment_callback(
    OrderTrackingId: str, OrderMerchantReference: str, db: Session = Depends(get_db)
):
    """
    Pesapal calls this URL after the user interacts with the payment page.
    """
    token = get_pesapal_token()
    status_data = get_transaction_status(token, OrderTrackingId)

    if status_data and status_data.get("status") == "200":
        payment_status = status_data.get(
            "payment_status_description"
        )  # e.g., "Completed"

        # Update your database
        transaction = (
            db.query(models.Transaction)
            .filter(models.Transaction.transaction_ref == OrderMerchantReference)
            .first()
        )

        if transaction:
            transaction.transaction_status = payment_status.upper()
            db.commit()

        return {"message": "Payment processed", "status": payment_status}

    return {"message": "Could not verify payment"}


@app.get("/api/v1/payments/check-status/{merchant_ref}")
def check_my_payment(merchant_ref: str, db: Session = Depends(get_db)):

    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_ref == merchant_ref)
        .first()
    )

    if not transaction:
        return {"error": "Transaction not found"}

    return {
        "reference": transaction.transaction_ref,
        "status": transaction.transaction_status,
        "amount": transaction.amount,
    }
