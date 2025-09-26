from __future__ import annotations
from typing import Optional
from core.db_connection import Database, get_db

class ClienteRepository:

    def __init__(self, db: Database):
        self.db = db

    def list_clientes(self, ativos: bool | None = True):
        sql = """
        SELECT id::text AS id, nome, cnpj, email
        FROM core.clientes
        WHERE (:ativos IS NULL OR is_ativo = :ativos)
        ORDER BY nome
        """
        return self.db.fetch_all(sql, {"ativos": ativos})

    def exists_by_cnpj(self, cnpj: str) -> bool:
        return bool(self.db.fetch_one("SELECT 1 FROM core.clientes WHERE cnpj = :c", {"c": cnpj}))

    def create(self, *, nome: str, email: str, cnpj: str, telefone: str, endereco: str) -> dict:
        sql = """
        INSERT INTO core.clientes (nome, email, cnpj, telefone, endereco)
        VALUES (:nome, :email, :cnpj, :telefone, :endereco)
        RETURNING id, nome, cnpj, email
        """

        return self.db.fetch_one_tx(sql, locals())
