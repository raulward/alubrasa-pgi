
from abc import ABC, abstractmethod
from typing import Optional, Any, List, Dict, Tuple
from uuid import UUID

class TaxRepositoryInterface(ABC):
    @abstractmethod
    async def get_pis(self) -> float:
        """Returns PIS tax rate (e.g., 0.65 or 0.0065 depends on impl, cleaned in Service)"""
        pass

    @abstractmethod
    async def get_cofins(self) -> float:
        """Returns COFINS tax rate"""
        pass

class NcmRepositoryInterface(ABC):
    @abstractmethod
    async def find_ncm_info(self, ncm_code: str) -> Optional[dict]:
        """Returns dict with NCM info (st, convenio, id, etc.) given a code"""
        pass

    @abstractmethod
    async def has_convenio(self, ncm_id: str, uf_destino: str) -> bool:
        """Checks if there is a convenio/protocolo for the given NCM ID and destination UF"""
        pass

    @abstractmethod
    async def find_id_by_ncm_code(self, ncm_code: str) -> Optional[str]:
        """Finds NCM ID (UUID) by code"""
        pass

class ItemRepositoryInterface(ABC):
    @abstractmethod
    async def bulk_insert(self, id_obra: str, rows: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Inserts multiple items.
        Returns: (success_count, list_of_error_dicts)
        """
        pass

    @abstractmethod
    async def list_items(self, id_obra: str) -> List[Dict[str, Any]]:
        """List all items for a given obra"""
        pass
