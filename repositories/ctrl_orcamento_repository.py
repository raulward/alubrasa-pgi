from core.db_connection import Database, get_db
from __future__ import annotations

class ControleOrcamentoRepository:
    def __init__(self, db: Database):
        self._db = get_db()

    def list_orcamentos(self):
        sql = """
        SELECT 
        """
