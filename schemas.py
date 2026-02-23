from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PaymentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    amount: float = Field(..., gt=0)
    phone: str


class PaymentResponse(BaseModel):
    reference: str
    redirect_url: str
    status: str

    class Config:
        from_attributes = True


class TransactionRecord(BaseModel):
    id: int
    amount: float
    phone: str
    transaction_ref: str
    transaction_status: str
    created_at: datetime

    class Config:
        from_attributes = True 


class PesapalIPN(BaseModel):
    OrderTrackingId: str
    OrderMerchantReference: str
    OrderNotificationType: str
