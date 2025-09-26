from __future__ import annotations
from core.db_connection import Database

class ObraRepository:
    def __init__(self, db: Database):
        self.db = db

    def exists_by_codigo(self, codigo: str) -> bool:
        return bool(self.db.fetch_one("SELECT 1 FROM obras WHERE codigo = :x", {"x": codigo}))

    def list_ativas(self) -> list[dict]:
        sql = """
        SELECT id::text AS id, nome, codigo
        FROM core.obras
        WHERE is_ativo = true
        ORDER BY nome
        """
        return self.db.fetch_all(sql)

    def create(self, *, id_cliente: str, nome: str, endereco: str, cnpj: str, codigo: str) -> dict:
        sql = """
        INSERT INTO core.obras (id_cliente, nome, endereco, cnpj, codigo)
        VALUES (:id_cliente, :nome, :endereco, :cnpj, :codigo)
        RETURNING id, nome, codigo
        """
        return self.db.fetch_one_tx(sql, locals())
