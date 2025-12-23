
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.frameworks.db.session import get_db
from src.interface_adapters.repositories.postgres_repository import PostgresTaxRepository, PostgresNcmRepository, PostgresItemRepository
from src.interface_adapters.repositories.postgres_construction_repository import PostgresConstructionRepository
from src.use_cases.pricing.calculate_price import CalculatePriceUseCase
from src.use_cases.items.import_items import ImportItemsUseCase
from src.use_cases.items.list_items import ListItemsUseCase
from src.use_cases.construction.create_item import CreateItemPlanejadoUseCase
from src.use_cases.construction.register_delivery import RegisterEntregaUseCase
from src.use_cases.construction.list_items import ListItemsByObraUseCase
from src.use_cases.construction.import_items import ImportConstructionItemsUseCase

async def get_pricing_use_case(session: AsyncSession = Depends(get_db)) -> CalculatePriceUseCase:
    tax_repo = PostgresTaxRepository(session)
    ncm_repo = PostgresNcmRepository(session)
    return CalculatePriceUseCase(tax_repo, ncm_repo)

async def get_import_items_use_case(session: AsyncSession = Depends(get_db)) -> ImportItemsUseCase:
    item_repo = PostgresItemRepository(session)
    return ImportItemsUseCase(item_repo)

async def get_list_items_use_case(session: AsyncSession = Depends(get_db)) -> ListItemsUseCase:
    item_repo = PostgresItemRepository(session)
    return ListItemsUseCase(item_repo)

async def get_construction_repo(session: AsyncSession = Depends(get_db)) -> PostgresConstructionRepository:
    return PostgresConstructionRepository(session)

async def get_create_item_planejado_use_case(
    repo: PostgresConstructionRepository = Depends(get_construction_repo)
) -> CreateItemPlanejadoUseCase:
    return CreateItemPlanejadoUseCase(repo)

async def get_register_entrega_use_case(
    repo: PostgresConstructionRepository = Depends(get_construction_repo)
) -> RegisterEntregaUseCase:
    return RegisterEntregaUseCase(repo)

async def get_list_items_by_obra_use_case(
    repo: PostgresConstructionRepository = Depends(get_construction_repo)
) -> ListItemsByObraUseCase:
    return ListItemsByObraUseCase(repo)

async def get_import_construction_items_use_case(
    repo: PostgresConstructionRepository = Depends(get_construction_repo)
) -> ImportConstructionItemsUseCase:
    return ImportConstructionItemsUseCase(repo)
