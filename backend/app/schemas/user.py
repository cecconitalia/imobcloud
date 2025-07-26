# Caminho: imobcloud/backend/app/schemas/user.py (NOVO FICHEIRO)

from pydantic import BaseModel, EmailStr

# Schema para o corpo do pedido de login
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema para os dados contidos dentro do token JWT
class TokenData(BaseModel):
    email: EmailStr | None = None

# Schema base para o utilizador
class UserBase(BaseModel):
    email: EmailStr

# Schema para criar um novo utilizador
class UserCreate(UserBase):
    password: str
    is_superuser: bool = False

# Schema para ler os dados de um utilizador da API (não expõe a senha)
class UserRead(UserBase):
    id: int
    is_superuser: bool

    class Config:
        from_attributes = True
