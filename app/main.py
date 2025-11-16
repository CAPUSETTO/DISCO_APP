from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine

# 👇 IMPORTANTE: importar modelos para que SQLAlchemy los registre
from app.models import user, ticket, cash  # noqa: F401

from app.routers import tickets, cash as cash_router


# Crear tablas al arrancar (para desarrollo)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Disco Entradas & Cajas")

app.include_router(tickets.router)
app.include_router(cash_router.router)