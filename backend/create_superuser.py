# Caminho: imobcloud/backend/create_superuser.py (ATUALIZADO)

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
import os

# Importamos os nossos modelos, funções de segurança e a Base declarativa
from app.models.user import User
from app.models.imobiliaria import Imobiliaria
from app.models.imovel import Imovel
from app.core.security import get_password_hash
from app.db.session import Base

# --- DADOS DO SUPER ADMIN ---
SUPERUSER_EMAIL = "admin@imobcloud.com"
SUPERUSER_PASSWORD = "adminpassword"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://imobuser:supersecret@db:5432/imobcloud_db")

async def init_db(engine):
    """Cria todas as tabelas no banco de dados se elas não existirem."""
    print("A verificar e criar tabelas, se necessário...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas prontas.")

async def create_superuser():
    print("A iniciar a criação do Super Admin...")
    
    engine = create_async_engine(DATABASE_URL)
    
    # --- ALTERAÇÃO AQUI ---
    # Primeiro, garantimos que todas as tabelas existem.
    await init_db(engine)

    AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

    async with AsyncSessionLocal() as db:
        # Verifica se o utilizador já existe para não dar erro
        result = await db.execute(select(User).where(User.email == SUPERUSER_EMAIL))
        existing_user = result.scalars().first()

        if existing_user:
            print(f"Utilizador com o email {SUPERUSER_EMAIL} já existe. Nenhuma ação foi tomada.")
            return

        # Cria o objeto do novo utilizador
        db_user = User(
            email=SUPERUSER_EMAIL,
            hashed_password=get_password_hash(SUPERUSER_PASSWORD),
            is_superuser=True,
        )
        
        db.add(db_user)
        await db.commit()

    print("---")
    print(f"Super Admin criado com sucesso!")
    print(f"Email: {SUPERUSER_EMAIL}")
    print(f"Senha: {SUPERUSER_PASSWORD}")
    print("---")

if __name__ == "__main__":
    asyncio.run(create_superuser())
