from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum

class TicketType(str, enum.Enum):
    SIN_CONSUMO = "SIN_CONSUMO"
    CON_CONSUMOS = "CON_CONSUMOS"
    CONSUMO_A_ELEGIR = "CONSUMO_A_ELEGIR"
    DINERO_TICKET = "DINERO_TICKET"
    DINERO_TARJETA = "DINERO_TARJETA"

class TicketStatus(str, enum.Enum):
    EMITIDA = "EMITIDA"
    USADA = "USADA"
    ANULADA = "ANULADA"

class PaymentMethod(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    MERCADOPAGO = "MERCADOPAGO"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, index=True, nullable=False)

    ticket_type = Column(Enum(TicketType), nullable=False)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.EMITIDA)

    base_price = Column(Numeric(10, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(10, 2), nullable=True)       # para DINERO_*
    remaining_credit = Column(Numeric(10, 2), nullable=True)

    payment_method = Column(Enum(PaymentMethod), nullable=False)
    rrpp_name = Column(String(100), nullable=True)

    issued_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)