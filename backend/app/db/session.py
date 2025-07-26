# Caminho: imobcloud/backend/app/db/session.py
# Lógica para criar a sessão com o banco de dados (SQLAlchemy)

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o motor de conexão assíncrono com o banco de dados
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Cria uma fábrica de sessões assíncronas
# expire_on_commit=False evita que os atributos dos objetos expirem após o commit
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base declarativa para os modelos do SQLAlchemy
Base = declarative_base()

# Função de dependência para obter uma sessão do banco de dados em cada request
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
