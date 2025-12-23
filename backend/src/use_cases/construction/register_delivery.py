
from src.use_cases.ports.construction_repository import ConstructionRepositoryInterface
from src.domain.entities.construction import EntregaRealizada
from src.frameworks.http.schemas.construction import EntregaRealizadaCreate

class RegisterEntregaUseCase:
    def __init__(self, repository: ConstructionRepositoryInterface):
        self.repository = repository

    async def execute(self, input_entrega: EntregaRealizadaCreate) -> EntregaRealizada:
        entrega_entity = EntregaRealizada(
            item_planejado_id=input_entrega.item_planejado_id,
            numero_nf=input_entrega.numero_nf,
            data_faturamento=input_entrega.data_faturamento,
            quantidade_entregue=input_entrega.quantidade_entregue
        )
        return await self.repository.create_entrega(entrega_entity)
