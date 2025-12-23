
import pandas as pd
import io
import unicodedata
from typing import List, Dict, Tuple, Any, Optional
from src.use_cases.ports.repositories import ItemRepositoryInterface
from src.use_cases.items.dtos import ImportResult
import logging

logger = logging.getLogger(__name__)

class ImportItemsUseCase:
    def __init__(self, item_repo: ItemRepositoryInterface):
        self.item_repo = item_repo

    async def execute(self, id_obra: str, file_bytes: bytes) -> ImportResult:
        logger.info(f"Starting import for obra {id_obra}")

        # 1. Parse Excel
        try:
            df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)
        except Exception as e:
            raise ValueError(f"Invalid Excel file: {str(e)}")

        # 2. Normalize Headers
        df_norm = self._normalize_headers(df_raw)
        rows = df_norm.to_dict(orient="records")

        # 3. Optimize Validation Loop (Pre-process)
        cleaned_rows: List[Dict[str, Any]] = []
        validation_errors: List[Dict[str, Any]] = []

        for idx, r in enumerate(rows, start=1):
            nr, errs = self._validate_and_normalize_row(r)
            if errs:
                validation_errors.append({"index": idx, "codigo": r.get("codigo"), "erros": errs})
            else:
                cleaned_rows.append(nr)

        if not cleaned_rows:
            return ImportResult(total_ok=0, errors=[], validation_errors=validation_errors)

        # 4. Persistence
        ok_count, db_errors = await self.item_repo.bulk_insert(id_obra=id_obra, rows=cleaned_rows)

        return ImportResult(
            total_ok=ok_count,
            errors=db_errors,
            validation_errors=validation_errors
        )

    def _normalize_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        # remove 'Unnamed'
        keep = [c for c in df.columns if not str(c).lower().startswith("unnamed")]
        df = df[keep].copy()

        # normaliza cabeçalho
        cols = [self._unaccent_lower(str(c)) for c in df.columns]
        df.columns = cols

        # renomeia equivalências (Legacy Logic)
        rename = {
            "peso_total": "peso",
            "r$ total": "preco_total",
            "valor total": "preco_total",
            "r$ unit": "preco_unit",
            "valor unit": "preco_unit",
            "desc": "descricao",
            "und": "unidade",
            "uni": "unidade",
            "categoria": "grupo",
            "qtd": "quantidade",
            "qtdade": "quantidade",
        }
        return df.rename(columns={c: rename.get(c, c) for c in df.columns})

    def _unaccent_lower(self, s: str) -> str:
        s = s.strip()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower().strip()

    def _validate_and_normalize_row(self, row: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        errs: List[str] = []

        # Helpers
        def clean_str(v): return str(v).strip() if v and not pd.isna(v) else ""
        def parse_num(v):
            if pd.isna(v) or v == "" or v is None: return None
            try: return float(v)
            except: return None

        codigo = clean_str(row.get("codigo"))
        descricao = clean_str(row.get("descricao"))
        unidade = clean_str(row.get("unidade"))
        grupo   = clean_str(row.get("grupo"))
        dimensoes = clean_str(row.get("dimensoes"))
        acabamento = clean_str(row.get("acabamento"))
        liga = clean_str(row.get("liga"))

        if not codigo:   errs.append("codigo vazio")
        if not descricao:errs.append("descricao vazia")
        if not unidade:  errs.append("unidade vazia")
        if not grupo:    errs.append("grupo vazio")

        quantidade = parse_num(row.get("quantidade"))
        preco_unit = parse_num(row.get("preco_unit"))
        preco_total= parse_num(row.get("preco_total"))
        peso       = parse_num(row.get("peso"))
        peso_unit  = parse_num(row.get("peso_unit"))

        if not quantidade or quantidade <= 0:
            errs.append("quantidade inválida (<=0)")

        # Calculations
        if quantidade:
            if preco_total is not None and preco_unit is None:
                preco_unit = preco_total / quantidade
            if preco_unit is not None and preco_total is None:
                preco_total = preco_unit * quantidade
            if peso is None and peso_unit is not None:
                peso = peso_unit * quantidade

        # Business Rule: Perfis
        if grupo.lower() == "perfis":
            if not liga:
                errs.append("liga obrigatória para perfis")
        else:
            acabamento = None
            liga = None

        if errs:
            return None, errs

        norm = {
            "codigo": codigo,
            "descricao": descricao,
            "unidade": unidade,
            "grupo": grupo,
            "dimensoes": dimensoes,
            "quantidade": quantidade,
            "peso": peso,
            "preco_unit": preco_unit,
            "preco_total": preco_total,
            "acabamento": acabamento,
            "liga": liga,
        }
        return norm, []
