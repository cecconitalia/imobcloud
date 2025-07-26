# Caminho: imobcloud/backend/app/models/imovel.py (ATUALIZADO)

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base
import datetime

class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- ALTERAÇÃO AQUI ---
    # Adicionamos a chave estrangeira para ligar o imóvel à imobiliária
    imobiliaria_id = Column(Integer, ForeignKey("imobiliarias.id"), nullable=False)
    
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    quartos = Column(Integer)
    banheiros = Column(Integer)
    area = Column(Integer)
    tipo = Column(String(50), nullable=False)

    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Define a relação para que possamos acessar os dados da imobiliária a partir de um imóvel
    imobiliaria = relationship("Imobiliaria")
