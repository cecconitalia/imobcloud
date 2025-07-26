# Caminho: imobcloud/backend/app/schemas/imobiliaria.py (NOVO ARQUIVO)

from pydantic import BaseModel, ConfigDict

class ImobiliariaBase(BaseModel):
    nome: str
    slug: str

class ImobiliariaCreate(ImobiliariaBase):
    pass

class ImobiliariaRead(ImobiliariaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

