from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.db.session import SessionLocal
from app.models.cash import (
    CashRegister,
    CashMovement,
    CashRegisterStatus,
    PaymentMethod,
)
from app.schemas.cash import (
    CashRegisterCreate,
    CashRegisterRead,
    CashMovementCreate,
    CashSummary,
)

router = APIRouter(prefix="/cash", tags=["cash"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/registers", response_model=CashRegisterRead)
def open_cash_register(data: CashRegisterCreate, db: Session = Depends(get_db)):
    # Podrías agregar lógica para evitar 2 cajas abiertas a la vez por usuario
    register = CashRegister(
        name=data.name,
        opening_balance=data.opening_balance,
        status=CashRegisterStatus.ABIERTA,
    )
    db.add(register)
    db.commit()
    db.refresh(register)
    return register

@router.post("/movements")
def create_movement(m: CashMovementCreate, db: Session = Depends(get_db)):
    register = db.get(CashRegister, m.cash_register_id)
    if not register or register.status != CashRegisterStatus.ABIERTA:
        raise HTTPException(status_code=400, detail="Caja no encontrada o cerrada")

    movement = CashMovement(**m.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return {"id": movement.id}

@router.post("/registers/{register_id}/close", response_model=CashRegisterRead)
def close_cash_register(register_id: int, db: Session = Depends(get_db)):
    register = db.get(CashRegister, register_id)
    if not register:
        raise HTTPException(status_code=404, detail="Caja no encontrada")

    # calcular saldo final (muy simple: apertura + suma movimientos)
    total = db.query(func.sum(CashMovement.amount)).filter(
        CashMovement.cash_register_id == register_id
    ).scalar() or 0

    register.closing_balance = register.opening_balance + total
    register.status = CashRegisterStatus.CERRADA
    register.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(register)
    return register

@router.get("/registers/{register_id}/summary", response_model=CashSummary)
def cash_summary(register_id: int, db: Session = Depends(get_db)):
    def total(pm: PaymentMethod) -> float:
        return (
            db.query(func.sum(CashMovement.amount))
            .filter(
                CashMovement.cash_register_id == register_id,
                CashMovement.payment_method == pm,
            )
            .scalar()
            or 0
        )

    ef = float(total(PaymentMethod.EFECTIVO))
    tj = float(total(PaymentMethod.TARJETA))
    mp = float(total(PaymentMethod.MERCADOPAGO))

    return CashSummary(
        total_efectivo=ef,
        total_tarjeta=tj,
        total_mercadopago=mp,
        total_general=ef + tj + mp,
    )