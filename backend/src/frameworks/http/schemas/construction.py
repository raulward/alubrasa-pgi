
from typing import List, Optional, Literal
from uuid import UUID
from datetime import date
from pydantic import BaseModel, ConfigDict

# --- Entregas ---

class EntregaRealizadaBase(BaseModel):
    numero_nf: Optional[str] = None
    data_faturamento: date
    quantidade_entregue: float

class EntregaRealizadaCreate(EntregaRealizadaBase):
    item_planejado_id: UUID

class EntregaRealizadaResponse(EntregaRealizadaBase):
    id: UUID
    item_planejado_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- Itens Planejados ---

class ItemPlanejadoBase(BaseModel):
    codigo_item: str
    descricao: Optional[str] = None
    unidade: Optional[str] = None
    grupo: Optional[str] = None
    cor: Optional[str] = None
    quantidade_total: float
    preco_venda_unitario: float
    categoria: Optional[Literal['PERFIL', 'COMPONENTE', 'VIDRO']] = None

class ItemPlanejadoCreate(ItemPlanejadoBase):
    obra_id: UUID

class ItemPlanejadoResponse(ItemPlanejadoBase):
    id: UUID
    obra_id: UUID
    entregas: List[EntregaRealizadaResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Obra (Minimal for listing relationships) ---

class ObraResponse(BaseModel):
    id: UUID
    nome: Optional[str] = None
    itens_planejados: List[ItemPlanejadoResponse] = []

    model_config = ConfigDict(from_attributes=True)
