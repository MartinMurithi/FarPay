from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Input Schema: What the android app will the to the server
class PaymentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    amount: float = Field(..., gt=0)
    phone: str


# Output Schema: What the server sends back to the app
class PaymentResponse(BaseModel):
    reference: str
    redirect_url: str
    status: str

    class Config:
        from_attributes = True


# History Schema: For viewing past transactions
class TransactionRecord(BaseModel):
    id: int
    amount: float
    phone: str
    transaction_ref: str
    transaction_status: str
    created_at: datetime

    class Config:
        from_attributes = True  # This is mandatory for DB-to-JSON conversion


class PesapalIPN(BaseModel):
    OrderTrackingId: str
    OrderMerchantReference: str
    OrderNotificationType: str
