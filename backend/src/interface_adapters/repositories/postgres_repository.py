
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import re

from src.use_cases.ports.repositories import TaxRepositoryInterface, NcmRepositoryInterface, ItemRepositoryInterface

class PostgresTaxRepository(TaxRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pis(self) -> float:
        result = await self.session.execute(
            text("SELECT tx FROM ref.taxas_tributarias WHERE descricao = 'PIS' LIMIT 1")
        )
        row = result.mappings().first()
        return float(row["tx"]) if row else 0.0

    async def get_cofins(self) -> float:
        result = await self.session.execute(
            text("SELECT tx FROM ref.taxas_tributarias WHERE descricao = 'COFINS' LIMIT 1")
        )
        row = result.mappings().first()
        return float(row["tx"]) if row else 0.0

class PostgresNcmRepository(NcmRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_ncm_info(self, ncm_code: str) -> Optional[dict]:
        # Tries to find by exact code first
        result = await self.session.execute(
            text("""
            SELECT id::text as id, ncm, st, cest, cst, aliquota, convenio
            FROM ref.ncm_map
            WHERE ncm = :ncm
            LIMIT 1
            """),
            {"ncm": ncm_code}
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def has_convenio(self, ncm_id: str, uf_destino: str) -> bool:
        if not ncm_id or not uf_destino:
            return False

        result = await self.session.execute(
            text("""
            SELECT 1
            FROM ref.ncm_convenio
            WHERE ncm_id = CAST(:id AS uuid)
              AND sigla_estado = :uf
            LIMIT 1
            """),
            {"id": ncm_id, "uf": uf_destino.upper()}
        )
        return bool(result.scalar())

    async def find_id_by_ncm_code(self, ncm_code: str) -> Optional[str]:
        # Equivalent to legacy regex search
        digits = re.sub(r"\D", "", ncm_code or "")
        if not digits:
            return None

        result = await self.session.execute(
            text("""
            SELECT id::text AS id
            FROM ref.ncm_map
            WHERE regexp_replace(ncm, '[^0-9]', '', 'g') = :ncm
            LIMIT 1
            """),
            {"ncm": digits}
        )
        val = result.scalar()
        return str(val) if val else None

class PostgresItemRepository(ItemRepositoryInterface):
    INSERT_SQL = """
    INSERT INTO sales.orcamento_itens (
      id_obra, codigo, descricao, unidade, grupo, dimensoes,
      quantidade, peso, preco_total, preco_unit, acabamento, liga
    ) VALUES (
      :id_obra, :codigo, :descricao, :unidade, :grupo, :dimensoes,
      :quantidade, :peso, :preco_total, :preco_unit, :acabamento, :liga
    )
    RETURNING id::text AS id
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_insert(self, id_obra: str, rows: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
        ok = 0
        erros: List[Dict[str, Any]] = []

        # Iterate over rows and insert one by one with savepoints
        for idx, r in enumerate(rows, start=1):
            try:
                async with self.session.begin_nested():
                    # prepare params
                    params = {**r, 'id_obra': id_obra}
                    await self.session.execute(text(self.INSERT_SQL), params)
                    ok += 1
            except IntegrityError as e:
                msg = str(e.orig)
                if "ux_itens_orcados_item" in msg or "unique" in msg.lower():
                    msg = "Item duplicado para a obra (grupo, código, dimensões, acabamento, liga)."
                elif "ck_itens_perfis_acab_liga" in msg:
                    msg = "Regra de perfis: 'liga' é obrigatória para perfis; outros grupos não devem ter acabamento/liga."
                erros.append({"index": idx, "codigo": r.get("codigo"), "erro": msg})
            except Exception as e:
                erros.append({"index": idx, "codigo": r.get("codigo"), "erro": str(e)})

        # Commit at the end of the batch (or let the caller commit)
        # In Clean Arch, usually the UoW or Service commits, but we are using session directly.
        # Since we use begin_nested, we need to ensure the outer transaction is committed eventually.
        # Here we just execute. The dependency injection `get_db` yields a session / transaction.
        return ok, erros

    async def list_items(self, id_obra: str) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            text("""
            SELECT id::text as id, codigo, descricao, unidade, grupo,
                   dimensoes, quantidade, preco_total, preco_unit
            FROM sales.orcamento_itens
            WHERE id_obra = :id_obra
            ORDER BY id
            """),
            {"id_obra": id_obra}
        )
        return [dict(row) for row in result.mappings()]
