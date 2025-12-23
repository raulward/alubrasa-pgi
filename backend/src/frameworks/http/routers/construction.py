
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from src.frameworks.http.schemas.construction import (
    ItemPlanejadoCreate,
    ItemPlanejadoResponse,
    EntregaRealizadaCreate,
    EntregaRealizadaResponse
)
from src.frameworks.http.dependencies import (
    get_create_item_planejado_use_case,
    get_register_entrega_use_case,
    get_list_items_by_obra_use_case
)
from src.use_cases.construction.create_item import CreateItemPlanejadoUseCase
from src.use_cases.construction.register_delivery import RegisterEntregaUseCase
from src.use_cases.construction.list_items import ListItemsByObraUseCase

router = APIRouter(prefix="/construction", tags=["Construction/Obras"])

@router.post("/items", response_model=ItemPlanejadoResponse, status_code=201)
async def create_item_planejado(
    item_in: ItemPlanejadoCreate,
    use_case: CreateItemPlanejadoUseCase = Depends(get_create_item_planejado_use_case)
):
    try:
        return await use_case.execute(item_in)
    except Exception as e:
        # Generic error handling for now; refine with custom exceptions later
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/obras/{obra_id}/items", response_model=List[ItemPlanejadoResponse])
async def list_items_by_obra(
    obra_id: UUID,
    use_case: ListItemsByObraUseCase = Depends(get_list_items_by_obra_use_case)
):
    return await use_case.execute(obra_id)

@router.post("/deliveries", response_model=EntregaRealizadaResponse, status_code=201)
async def register_delivery(
    entrega_in: EntregaRealizadaCreate,
    use_case: RegisterEntregaUseCase = Depends(get_register_entrega_use_case)
):
    try:
        return await use_case.execute(entrega_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
