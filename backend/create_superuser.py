import asyncio
import os
import sys

# Adiciona o diretório da aplicação '/app' ao caminho do Python
sys.path.append('/app')

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# --- IMPORTAÇÕES CORRIGIDAS ---
from app.models.user import User
from app.core.security import get_password_hash
# -----------------------------

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@imobcloud.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword")

async def main():
    print("Connecting to the database...")
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        print(f"Checking if superuser '{ADMIN_EMAIL}' exists...")
        query = select(User).where(User.email == ADMIN_EMAIL)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            print("User not found. Creating new superuser...")
            new_user = User(
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_superuser=True,
            )
            session.add(new_user)
            await session.commit()
            print(f"✅ Superuser '{ADMIN_EMAIL}' created successfully.")
        else:
            print(f"✅ Superuser '{ADMIN_EMAIL}' already exists.")
    
    await engine.dispose()
    print("Process finished.")

if __name__ == "__main__":
    asyncio.run(main())