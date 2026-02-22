import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Transaction(Base):
    """
    Represents a payment transaction in the PostgreSQL database.

    This class maps directly to a table named 'transactions'.
    Each instance of this class represents a single row in that table.
    """

    __tablename__ = "transactions"

    # ID for each row
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    phone = Column(String, nullable=False)
    # Internal id to track payment status with Payment service
    transaction_ref = Column(String, unique=True, index=True, nullable=False)
    transaction_status = Column(String, default="PENDING")
    # Audit trail: When was this transaction first created?
    created_at = Column(DateTime, default=datetime.datetime.now())
