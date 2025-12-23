
from uuid import UUID
from src.use_cases.ports.construction_repository import ConstructionRepositoryInterface
from src.domain.entities.construction import ItemPlanejado
from src.frameworks.http.schemas.construction import ItemPlanejadoCreate

class CreateItemPlanejadoUseCase:
    def __init__(self, repository: ConstructionRepositoryInterface):
        self.repository = repository

    async def execute(self, input_item: ItemPlanejadoCreate) -> ItemPlanejado:
        # Create Entity from DTO/Schema input
        item_entity = ItemPlanejado(
            obra_id=input_item.obra_id,
            codigo_item=input_item.codigo_item,
            descricao=input_item.descricao,
            unidade=input_item.unidade,
            quantidade_total=input_item.quantidade_total,
            preco_venda_unitario=input_item.preco_venda_unitario,
            categoria=input_item.categoria
        )
        return await self.repository.create_item_planejado(item_entity)
