# Caminho: imobcloud/backend/app/models/imobiliaria.py (NOVO ARQUIVO)

from sqlalchemy import Column, Integer, String
from ..db.session import Base

class Imobiliaria(Base):
    __tablename__ = "imobiliarias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    # Usaremos isso no futuro para os subdomínios, ex: 'minha-imob'
    slug = Column(String(100), nullable=False, unique=True) 
