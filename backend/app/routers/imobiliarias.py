# Caminho: imobcloud/backend/app/routers/imobiliarias.py (ATUALIZADO)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..db.session import get_db
from ..models.imobiliaria import Imobiliaria
from ..schemas.imobiliaria import ImobiliariaCreate, ImobiliariaRead
from ..core.dependencies import get_current_superuser

# Router para ações de administração, protegido por login de Super Admin
router_admin = APIRouter(
    prefix="/imobiliarias",
    tags=["Imobiliárias (Admin Protegido)"],
    dependencies=[Depends(get_current_superuser)],
    responses={404: {"description": "Não encontrado"}},
)

# --- NOVO ROUTER PÚBLICO ---
# Router para ações públicas, que não exigem login
router_publico = APIRouter(
    prefix="/public/imobiliarias",
    tags=["Imobiliárias (Público)"],
    responses={404: {"description": "Não encontrado"}},
)

@router_admin.post("/", response_model=ImobiliariaRead, status_code=201)
async def criar_imobiliaria(
    imobiliaria: ImobiliariaCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Cria uma nova imobiliária. Apenas para Super Admins.
    """
    nova_imobiliaria = Imobiliaria(**imobiliaria.dict())
    db.add(nova_imobiliaria)
    await db.commit()
    await db.refresh(nova_imobiliaria)
    return nova_imobiliaria

@router_admin.get("/", response_model=List[ImobiliariaRead])
async def listar_imobiliarias(
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as imobiliárias cadastradas. Apenas para Super Admins.
    """
    result = await db.execute(select(Imobiliaria).offset(0).limit(100))
    imobiliarias = result.scalars().all()
    return imobiliarias

# --- NOVO ENDPOINT PÚBLICO ---
@router_publico.get("/slug/{slug}", response_model=ImobiliariaRead)
async def ler_imobiliaria_por_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Busca os detalhes de uma imobiliária pelo seu slug.
    """
    result = await db.execute(select(Imobiliaria).where(Imobiliaria.slug == slug))
    imobiliaria = result.scalars().first()
    if imobiliaria is None:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    return imobiliaria
