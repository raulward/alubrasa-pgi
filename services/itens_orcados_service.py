from __future__ import annotations
from utils.validators import Validator
from typing import Any, Dict, List, Tuple, Optional
from repositories.itens_orcados_repository import ItensOrcadosRepository
import pandas as pd
import unicodedata
import io


class ItensOrcadosService:
    def __init__(self, repository: ItensOrcadosRepository):
        self.repo = repository
        self.validator = Validator()

    def list_itens():
        return ItensOrcadosRepository.list_itens()

    def unaccent_lower(self, s: str) -> str:
        s = str(s or "").strip()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower().strip()

    def build_template_bytes(self) -> bytes:
        cols = [
            "codigo", "descricao", "liga", "acabamento", "grupo",
            "unidade", "dimensoes", "quantidade", "peso_total",
            "preco_total", "peso_unit", "preco_unit"
        ]
        df = pd.DataFrame([{c: "" for c in cols}])
        df.loc[0, "codigo"] = "AL-1234"
        df.loc[0, "descricao"] = "Perfil U"
        df.loc[0, "liga"] = "6063"     # perfis: obrigatória
        df.loc[0, "acabamento"] = ""   # perfis: opcional
        df.loc[0, "grupo"] = "perfis"
        df.loc[0, "unidade"] = "un"
        df.loc[0, "dimensoes"] = "6m"
        df.loc[0, "quantidade"] = 120

        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="itens")
            info = pd.DataFrame({
                "coluna": cols,
                "descricao": [
                    "Código (obrigatório)",
                    "Descrição (obrigatório)",
                    "Liga (obrigatória em 'perfis'; vazia nos demais)",
                    "Acabamento (opcional em 'perfis'; vazio nos demais)",
                    "Grupo (perfis, acm, selantes, guarnicoes, parafusos)",
                    "Unidade (ex.: un, kg, m)",
                    "Dimensões/medidas (opcional)",
                    "Quantidade (>0)",
                    "Peso total (kg) (opcional; pode vir de peso_unit * quantidade)",
                    "Preço total (R$) (opcional)",
                    "Peso unitário (kg) (opcional, para calcular peso total)",
                    "Preço unitário (R$) (opcional; usado para calcular o total)"
                ]
            })
            info.to_excel(writer, index=False, sheet_name="LEIA-ME")
        return bio.getvalue()

    def _normalize_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        # remove 'Unnamed'
        keep = [c for c in df.columns if not str(c).lower().startswith("unnamed")]
        df = df[keep].copy()

        # normaliza cabeçalho
        cols = [self.unaccent_lower(c) for c in df.columns]
        df.columns = cols

        # renomeia equivalências
        rename = {
            "peso_total": "peso",       # alinhado ao banco
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

    def preview_dataframe(self, file_bytes: bytes, limit: int = 200) -> pd.DataFrame:
        df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)
        df_norm = self._normalize_headers(df_raw)
        return df_norm.head(limit)

    def _normalize_row(self, row: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Recebe uma linha da planilha e devolve (row_normalizada, erros_da_linha).
        """
        errs: List[str] = []
        codigo = self.validator.clean_str(row.get("codigo"))
        descricao = self.validator.clean_str(row.get("descricao"))
        unidade = self.validator.clean_str(row.get("unidade"))
        grupo   = self.validator.clean_str(row.get("grupo"))
        dimensoes = self.validator.clean_str(row.get("dimensoes"))
        acabamento = self.validator.clean_str(row.get("acabamento"))
        liga = self.validator.clean_str(row.get("liga"))

        if not codigo:   errs.append("codigo vazio")
        if not descricao:errs.append("descricao vazia")
        if not unidade:  errs.append("unidade vazia")
        if not grupo:    errs.append("grupo vazio")

        quantidade = self.validator.parse_num(row.get("quantidade"))
        preco_unit = self.validator.parse_num(row.get("preco_unit"))
        preco_total= self.validator.parse_num(row.get("preco_total"))
        peso       = self.validator.parse_num(row.get("peso"))
        peso_unit  = self.validator.parse_num(row.get("peso_unit"))  # pode vir na planilha

        if not quantidade or quantidade <= 0:
            errs.append("quantidade inválida (<=0)")

        # calcula preços se faltar um deles
        if quantidade and preco_total is not None and preco_unit is None:
            preco_unit = preco_total / quantidade
        if quantidade and preco_unit is not None and preco_total is None:
            preco_total = preco_unit * quantidade

        # calcula peso total a partir de peso_unit, se necessário
        if peso is None and peso_unit is not None and quantidade and quantidade > 0:
            peso = peso_unit * quantidade

        # regra dos perfis
        if grupo.lower() == "perfis":
            if not liga:
                errs.append("liga obrigatória para perfis")
            # acabamento pode ser None
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

    def import_file(self, *, id_obra: str, file_bytes: bytes) -> Tuple[int, List[Dict[str,Any]], List[Dict[str,Any]]]:
        df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)
        df_norm = self._normalize_headers(df_raw)
        rows = df_norm.to_dict(orient="records")
        ok, db_errors, val_errors = self.create_many(id_obra=id_obra, rows=rows)
        return ok, db_errors, val_errors

    def create(self, **kwargs) -> Dict[str, Any]:
        row, errs = self._normalize_row(kwargs)
        if errs:
            raise ValueError(" / ".join(errs))
        ok, errors = self.repo.bulk_insert(id_obra=kwargs["id_obra"], rows=[row])
        if ok == 1:
            return {"ok": True}
        raise ValueError(errors[0]["erro"] if errors else "Falha ao inserir item")

    def create_many(self, *, id_obra: str, rows: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]], List[Dict[str, Any]]]:

        cleaned: List[Dict[str, Any]] = []
        val_errors: List[Dict[str, Any]] = []

        for idx, r in enumerate(rows, start=1):
            nr, errs = self._normalize_row(r)
            if errs:
                val_errors.append({"index": idx, "codigo": r.get("codigo"), "erros": errs})
            else:
                cleaned.append(nr)

        if not cleaned:
            return 0, [], val_errors

        ok, db_errors = self.repo.bulk_insert(id_obra=id_obra, rows=cleaned)
        return ok, db_errors, val_errors
