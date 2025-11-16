from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketRead
from sqlalchemy import func

router = APIRouter(prefix="/tickets", tags=["tickets"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def next_ticket_number(db: Session) -> int:
    last = db.query(func.max(Ticket.number)).scalar()
    return (last or 0) + 1

@router.post("/", response_model=TicketRead)
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    number = next_ticket_number(db)
    remaining_credit = ticket_in.credit_amount
    db_ticket = Ticket(
        number=number,
        remaining_credit=remaining_credit,
        **ticket_in.model_dump()
    )
    db.add(db_ticket)
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