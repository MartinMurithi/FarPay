import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Transaction(Base):
    """
    Represents a payment transaction in the PostgreSQL database.

    This class maps directly to a table named 'transactions'.
    Each instance of this class represents a single row in that table.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    # Internal id to track payment status with Payment service
    transaction_ref: Mapped[str] = mapped_column(String, unique=True, index=True)
    transaction_status: Mapped[str] = mapped_column(String, default="PENDING")
    # Audit trail: When was this transaction first created?
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
