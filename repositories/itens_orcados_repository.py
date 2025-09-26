from __future__ import annotations
from typing import Iterable, Tuple, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from core.db_connection import Database, get_db

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

class ItensOrcadosRepository:
    def __init__(self, db: Database):
        self.db = db

    def list_itens(self):
        db = get_db()
        sql = """
        SELECT id::text AS id, nome, codigo
        FROM core.obras
        WHERE is_ativo = true
        ORDER BY nome
        """
        return db.fetch_all(sql)

    def bulk_insert(self, *, id_obra: str, rows: Iterable[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
        ok = 0
        erros: List[Dict[str, Any]] = []
        with self.db.engine.begin() as conn:
            for idx, r in enumerate(rows, start=1):
                try:
                    with conn.begin_nested():
                        conn.execute(text(INSERT_SQL), {**r, 'id_obra': id_obra}).mappings().first()
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
        return ok, erros
