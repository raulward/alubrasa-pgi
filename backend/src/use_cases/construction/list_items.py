
from typing import List
from uuid import UUID
from src.use_cases.ports.construction_repository import ConstructionRepositoryInterface
from src.domain.entities.construction import ItemPlanejado

class ListItemsByObraUseCase:
    def __init__(self, repository: ConstructionRepositoryInterface):
        self.repository = repository

    async def execute(self, obra_id: UUID) -> List[ItemPlanejado]:
        return await self.repository.get_itens_by_obra(obra_id)
