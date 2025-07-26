# Caminho: imobcloud/backend/app/models/user.py (NOVO FICHEIRO)

from sqlalchemy import Column, Integer, String, Boolean
from ..db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean(), default=False)
