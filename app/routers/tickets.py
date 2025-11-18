from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.ticket import Ticket, TicketStatus, PaymentMethod as TicketPaymentMethod
from app.schemas.ticket import TicketCreate, TicketRead

# 👇 Importamos modelos de caja para crear el movimiento automáticamente
from app.models.cash import (
    CashMovement,
    CashMovementType,
    PaymentMethod as CashPaymentMethod,
    CashRegister,
    CashRegisterStatus,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Obtiene el siguiente número de ticket
def next_ticket_number(db: Session) -> int:
    last = db.query(func.max(Ticket.number)).scalar()
    return (last or 0) + 1


# Devuelve la última caja abierta
def get_open_cash_register(db: Session) -> CashRegister | None:
    return (
        db.query(CashRegister)
        .filter(CashRegister.status == CashRegisterStatus.ABIERTA)
        .order_by(CashRegister.opened_at.desc())
        .first()
    )


@router.post("/", response_model=TicketRead)
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    number = next_ticket_number(db)
    remaining_credit = ticket_in.credit_amount

    # 1) Crear el ticket (qr_code se genera solo por default en el modelo)
    db_ticket = Ticket(
        number=number,
        remaining_credit=remaining_credit,
        **ticket_in.model_dump(),
    )
    db.add(db_ticket)

    # 2) Buscar caja abierta
    cash_register = get_open_cash_register(db)
    if cash_register is None:
        raise HTTPException(
            status_code=400,
            detail="No hay ninguna caja abierta para registrar la venta del ticket.",
        )

    # 3) Convertir método de pago de ticket → método de pago de caja
    cash_payment_method = CashPaymentMethod[ticket_in.payment_method.name]

    # 4) Crear movimiento automático
    movement = CashMovement(
        cash_register_id=cash_register.id,
        movement_type=CashMovementType.VENTA,
        payment_method=cash_payment_method,
        amount=ticket_in.base_price,
        reference=f"ticket {number}",
    )

    db.add(movement)

    # 5) Guardar todo junto
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


@router.get("/", response_model=List[TicketRead])
def list_tickets(status: TicketStatus | None = None, db: Session = Depends(get_db)):
    q = db.query(Ticket)
    if status:
        q = q.filter(Ticket.status == status)
    return q.order_by(Ticket.issued_at.desc()).all()


@router.post("/{ticket_id}/use", response_model=TicketRead)
def use_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.status != TicketStatus.EMITIDA:
        raise HTTPException(status_code=400, detail="Ticket no está en estado EMITIDA")
    from datetime import datetime

    ticket.status = TicketStatus.USADA
    ticket.used_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/cancel", response_model=TicketRead)
def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.status == TicketStatus.USADA:
        raise HTTPException(status_code=400, detail="Ticket ya usada")
    ticket.status = TicketStatus.ANULADA
    db.commit()
    db.refresh(ticket)
    return ticket


# 🚀 NUEVO: Validar ticket por QR / código secreto
@router.post("/validate-by-code", response_model=TicketRead)
def validate_ticket_by_code(code: str, db: Session = Depends(get_db)):
    """
    Recibe un 'code' (el valor del qr_code del ticket).
    - Si el ticket existe y está EMITIDA → la marca como USADA.
    - Si está USADA o ANULADA → lanza error.
    """
    ticket = db.query(Ticket).filter(Ticket.qr_code == code).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if ticket.status == TicketStatus.USADA:
        raise HTTPException(status_code=400, detail="Ticket ya fue usada")

    if ticket.status == TicketStatus.ANULADA:
        raise HTTPException(status_code=400, detail="Ticket está anulada")

    from datetime import datetime
    ticket.status = TicketStatus.USADA
    ticket.used_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket