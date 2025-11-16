from pydantic import BaseModel
from datetime import datetime
from app.models.cash import (
    CashMovementType,
    PaymentMethod,
    CashRegisterStatus,
)

class CashRegisterCreate(BaseModel):
    name: str
    opening_balance: float

class CashRegisterRead(BaseModel):
    id: int
    name: str
    opening_balance: float
    closing_balance: float | None
    status: CashRegisterStatus
    opened_at: datetime
    closed_at: datetime | None

    class Config:
        from_attributes = True

class CashMovementCreate(BaseModel):
    cash_register_id: int
    movement_type: CashMovementType
    payment_method: PaymentMethod
    amount: float
    reference: str | None = None

class CashSummary(BaseModel):
    total_efectivo: float
    total_tarjeta: float
    total_mercadopago: float
    total_general: float