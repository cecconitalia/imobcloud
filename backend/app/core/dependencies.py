# Caminho: imobcloud/backend/app/core/dependencies.py (NOVO FICHEIRO)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

from ..db.session import get_db
from ..models.user import User
from ..schemas.user import TokenData
from .security import SECRET_KEY, ALGORITHM

# Isto diz ao FastAPI para procurar o token no cabeçalho 'Authorization'
# e que a página de login está em /token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Dependência que decodifica o token, valida e retorna o utilizador do banco de dados.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependência que verifica se o utilizador atual é um Super Admin.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O utilizador não tem privilégios suficientes"
        )
    return current_user
