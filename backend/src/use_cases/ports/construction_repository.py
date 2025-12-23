
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.entities.construction import Obra, ItemPlanejado, EntregaRealizada

class ConstructionRepositoryInterface(ABC):
    @abstractmethod
    async def create_obra(self, obra: Obra) -> Obra:
        pass

    @abstractmethod
    async def get_obra_by_id(self, obra_id: UUID) -> Optional[Obra]:
        pass

    @abstractmethod
    async def create_item_planejado(self, item: ItemPlanejado) -> ItemPlanejado:
        pass

    @abstractmethod
    async def get_itens_by_obra(self, obra_id: UUID) -> List[ItemPlanejado]:
        pass

    @abstractmethod
    async def get_item_by_id(self, item_id: UUID) -> Optional[ItemPlanejado]:
        pass

    @abstractmethod
    async def create_entrega(self, entrega: EntregaRealizada) -> EntregaRealizada:
        pass

    @abstractmethod
    async def get_entregas_by_item(self, item_id: UUID) -> List[EntregaRealizada]:
        pass
