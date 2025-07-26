# Caminho: imobcloud/backend/app/main.py (VERSÃO CORRETA)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.session import engine, Base
# Importamos os módulos dos routers
from .routers import imoveis as imoveis_router
from .routers import imobiliarias as imobiliarias_router
from .routers import auth

# Importamos todos os modelos para que as tabelas sejam criadas
from .models.imobiliaria import Imobiliaria
from .models.imovel import Imovel
from .models.user import User

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="ImobCloud API",
    description="API para o sistema ImobCloud.",
    version="0.1.0"
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await create_tables()

# Incluímos todos os routers na aplicação
app.include_router(auth.router)
app.include_router(imobiliarias_router.router_admin)
app.include_router(imobiliarias_router.router_publico)
app.include_router(imoveis_router.router_imobiliaria)
app.include_router(imoveis_router.router_geral)


@app.get("/")
async def root():
    return {"message": "Bem-vindo à API ImobCloud!"}
