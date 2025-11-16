from pydantic import BaseModel
from datetime import datetime
from app.models.ticket import TicketType, TicketStatus, PaymentMethod

class TicketBase(BaseModel):
    ticket_type: TicketType
    base_price: float
    credit_amount: float | None = None
    payment_method: PaymentMethod
    rrpp_name: str | None = None

class TicketCreate(TicketBase):
    pass

class TicketRead(TicketBase):
    id: int
    number: int
    status: TicketStatus
    remaining_credit: float | None = None
    issued_at: datetime
    used_at: datetime | None = None

    class Config:
        from_attributes = True