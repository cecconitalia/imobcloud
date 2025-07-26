# Caminho: imobcloud/backend/app/routers/imoveis.py (ATUALIZADO)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..db.session import get_db
from ..models.imovel import Imovel
from ..schemas.imovel import ImovelCreate, ImovelRead

# --- NOVO ROUTER INDEPENDENTE ---
# Criamos um novo router para operações que não dependem de uma imobiliária específica no URL.
router_geral = APIRouter()

@router_geral.get("/imoveis/{imovel_id}", response_model=ImovelRead)
async def ler_imovel_por_id(imovel_id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca um único imóvel pelo seu ID.
    """
    result = await db.execute(select(Imovel).where(Imovel.id == imovel_id))
    imovel = result.scalars().first()
    if imovel is None:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return imovel


# --- ROUTER ANTIGO (AGORA RENOMEADO) ---
# Este continua a funcionar para criar e listar imóveis DENTRO de uma imobiliária.
router_imobiliaria = APIRouter(
    prefix="/imobiliarias/{imobiliaria_id}/imoveis",
    tags=["Imóveis (por Imobiliária)"],
    responses={404: {"description": "Não encontrado"}},
)

@router_imobiliaria.post("/", response_model=ImovelRead, status_code=201)
async def criar_imovel_para_imobiliaria(
    imobiliaria_id: int, 
    imovel: ImovelCreate, 
    db: AsyncSession = Depends(get_db)
):
    novo_imovel = Imovel(**imovel.dict(), imobiliaria_id=imobiliaria_id)
    db.add(novo_imovel)
    await db.commit()
    await db.refresh(novo_imovel)
    return novo_imovel


@router_imobiliaria.get("/", response_model=List[ImovelRead])
async def listar_imoveis_da_imobiliaria(
    imobiliaria_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Imovel)
        .where(Imovel.imobiliaria_id == imobiliaria_id)
        .offset(skip)
        .limit(limit)
    )
    imoveis = result.scalars().all()
    return imoveis
