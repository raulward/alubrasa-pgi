# repositories/precificacao_repository.py
from __future__ import annotations

import re
from typing import Any, Optional
from core.db_connection import get_db, Database


class PrecificacaoRepository:
    """
    Lê taxas (PIS/COFINS), resolve convênio por NCM (UUID) e lista UFs.
    """

    def __init__(self, db: Optional[Database] = None):
        self._db = db or get_db()

    # -------- TAXAS --------
    def get_pis(self):
        return self._db.fetch_one(
            "SELECT tx FROM ref.taxas_tributarias WHERE descricao = 'PIS' LIMIT 1"
        )

    def get_cofins(self):
        return self._db.fetch_one(
            "SELECT tx FROM ref.taxas_tributarias WHERE descricao = 'COFINS' LIMIT 1"
        )

    # alias opcional (retrocompatibilidade)
    def get_confins(self):
        return self.get_cofins()

    # -------- CONVÊNIO POR NCM/UF --------
    def find_convenio(self, ncm: Any, uf: str) -> bool:
        """
        True se há convênio/protocolo ST para (ncm_id, UF).
        Aceita dict (com 'id'/'ncm_id' ou 'ncm'/'codigo'/'code') ou string (código).
        Compara UUID com UUID via CAST(:id AS uuid).
        """
        if not ncm or not uf:
            return False

        # resolver ncm_id (UUID texto)
        ncm_id: Optional[str] = None
        if isinstance(ncm, dict):
            maybe_id = ncm.get("id") or ncm.get("ncm_id")
            if maybe_id:
                ncm_id = str(maybe_id)
            else:
                code = ncm.get("ncm") or ncm.get("codigo") or ncm.get("code")
                if code:
                    ncm_id = self.find_id_by_ncm_code(code)
        else:
            ncm_id = self.find_id_by_ncm_code(str(ncm))

        if not ncm_id:
            return False

        row = self._db.fetch_one(
            """
            SELECT 1
            FROM ref.ncm_convenio
            WHERE ncm_id = CAST(:id AS uuid)
              AND sigla_estado = :uf
            LIMIT 1
            """,
            {"id": ncm_id, "uf": uf.upper()},
        )
        return bool(row)

    def find_id_by_ncm_code(self, ncm_code: str) -> Optional[str]:
        """
        Retorna o UUID (texto) do NCM a partir do código (com/sem pontuação).
        """
        digits = re.sub(r"\D", "", ncm_code or "")
        if not digits:
            return None

        row = self._db.fetch_one(
            """
            SELECT id::text AS id
            FROM ref.ncm_map
            WHERE regexp_replace(ncm, '[^0-9]', '', 'g') = :ncm
            LIMIT 1
            """,
            {"ncm": digits},
        )
        return row["id"] if row else None

    # -------- UFs --------
    def list_ufs(self):
        sql = """
        SELECT sigla_estado
        FROM ref.estados
        WHERE sigla_estado IS NOT NULL
        ORDER BY sigla_estado
        """
        return self._db.fetch_all(sql)
