
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.use_cases.ports.construction_repository import ConstructionRepositoryInterface
from src.domain.entities.construction import Obra, ItemPlanejado, EntregaRealizada

class PostgresConstructionRepository(ConstructionRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_obra(self, obra: Obra) -> Obra:
        self.session.add(obra)
        await self.session.commit()
        await self.session.refresh(obra)
        return obra

    async def get_obra_by_id(self, obra_id: UUID) -> Optional[Obra]:
        result = await self.session.execute(
            select(Obra)
            .where(Obra.id == obra_id)
            .options(selectinload(Obra.itens_planejados))
        )
        return result.scalars().first()

    async def create_item_planejado(self, item: ItemPlanejado) -> ItemPlanejado:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_itens_by_obra(self, obra_id: UUID) -> List[ItemPlanejado]:
        result = await self.session.execute(
            select(ItemPlanejado)
            .where(ItemPlanejado.obra_id == obra_id)
            .options(selectinload(ItemPlanejado.entregas))
        )
        return list(result.scalars().all())

    async def get_item_by_id(self, item_id: UUID) -> Optional[ItemPlanejado]:
         result = await self.session.execute(
            select(ItemPlanejado)
            .where(ItemPlanejado.id == item_id)
            .options(selectinload(ItemPlanejado.entregas))
        )
         return result.scalars().first()

    async def create_entrega(self, entrega: EntregaRealizada) -> EntregaRealizada:
        self.session.add(entrega)
        await self.session.commit()
        await self.session.refresh(entrega)
        return entrega

    async def get_entregas_by_item(self, item_id: UUID) -> List[EntregaRealizada]:
        result = await self.session.execute(
            select(EntregaRealizada).where(EntregaRealizada.item_planejado_id == item_id)
        )
        return list(result.scalars().all())

    async def create_items_bulk(self, items: List[ItemPlanejado]) -> List[ItemPlanejado]:
        self.session.add_all(items)
        await self.session.commit()
        # We might not be able to refresh all easily without re-fetching,
        # but usually import doesn't require immediate ID return for all.
        return items
