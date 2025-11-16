from sqlalchemy import Column, Integer, String, Enum
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    CAJA = "CAJA"
    GERENCIA = "GERENCIA"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CAJA)