
from typing import List, Dict, Any
from src.use_cases.ports.repositories import ItemRepositoryInterface
import logging

logger = logging.getLogger(__name__)

class ListItemsUseCase:
    def __init__(self, item_repo: ItemRepositoryInterface):
        self.item_repo = item_repo

    async def execute(self, id_obra: str) -> List[Dict[str, Any]]:
        return await self.item_repo.list_items(id_obra)
