from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum


class CashRegisterStatus(str, enum.Enum):
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"


class CashMovementType(str, enum.Enum):
    VENTA = "VENTA"
    EXTRACCION = "EXTRACCION"
    INGRESO = "INGRESO"
    DEVOLUCION = "DEVOLUCION"


class PaymentMethod(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    MERCADOPAGO = "MERCADOPAGO"


class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    opening_balance = Column(Numeric(10, 2), nullable=False, default=0)
    closing_balance = Column(Numeric(10, 2), nullable=True)

    status = Column(
        Enum(CashRegisterStatus, name="cash_register_status"),
        nullable=False,
        default=CashRegisterStatus.ABIERTA,
    )

    # 👇 Si NO tenés todavía la tabla users, sacá el ForeignKey
    opened_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    opened_by = relationship("User", lazy="joined")


class CashMovement(Base):
    __tablename__ = "cash_movements"

    id = Column(Integer, primary_key=True, index=True)
    cash_register_id = Column(Integer, ForeignKey("cash_registers.id"), nullable=False)
    movement_type = Column(
        Enum(CashMovementType, name="cash_movement_type"),
        nullable=False,
    )
    payment_method = Column(
        Enum(PaymentMethod, name="cash_payment_method"),
        nullable=False,
    )
    amount = Column(Numeric(10, 2), nullable=False)
    reference = Column(String(100), nullable=True)  # por ej. nro de entrada
    created_at = Column(DateTime, default=datetime.utcnow)

    cash_register = relationship("CashRegister", lazy="joined")