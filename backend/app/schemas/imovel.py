# Caminho: imobcloud/backend/app/schemas/imovel.py
# Esquemas Pydantic para validação de dados de imóveis (request/response)

from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime
from decimal import Decimal

# Schema base com os campos comuns
class ImovelBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    preco: Decimal
    quartos: int
    banheiros: int
    area: int
    tipo: str

# Schema para criação de um novo imóvel (o que a API recebe no POST)
class ImovelCreate(ImovelBase):
    pass

# Schema para leitura de um imóvel (o que a API retorna no GET)
# Inclui campos que são gerados pelo banco, como o ID.
class ImovelRead(ImovelBase):
    id: int
    data_criacao: datetime.datetime

    # --- ALTERAÇÃO AQUI ---
    # 'orm_mode = True' foi substituído por 'from_attributes = True'
    # dentro de um `model_config` para ser compatível com Pydantic V2.
    model_config = ConfigDict(from_attributes=True)

