from __future__ import annotations
from repositories.mapeamento_nfs_repository import MapeamentoNFSRepository
from utils.validators import Validator
import pandas as pd


class MapeamentoNFSService:
    def __init__(self, repo=None, db=None):
        # Se já vier um repo injetado, usa e sai.
        if repo is not None:
            self._repo = repo
            return

        # Constrói o repo padrão garantindo que o DB exista SEMPRE.
        from repositories.mapeamento_nfs_repository import MapeamentoNFSRepository
        if db is None:
            from core.db_connection import get_db
            local_db = get_db()
        else:
            local_db = db

        self._repo = MapeamentoNFSRepository(local_db)

    def list_descricoes(self):
        rows = self._repo.list_descricoes()
        descricoes = {
            (r.get("descricao") or "").strip()
            for r in rows
            if r.get("descricao")
        }
        return sorted(descricoes)

    def list_estados(self):
        rows = self._repo.list_estados()
        estados = {
            (r.get("estado") or "").strip()
            for r in rows
            if r.get("estado")
        }
        return sorted(estados)

    def list_ncms(self):
        list_ncms_dict = self._repo.list_ncms()
        list_ncms_code = [code['ncm'] for code in list_ncms_dict]
        return list_ncms_code

    def find_cfop(self, desc: str, estado: str):
        return self._repo.find_cfop(desc, estado)

    def find_ncm(self, ncm: str):
        return self._repo.find_ncm(ncm)

    def combination(self, desc: str, ncm: str, estado: str):
        cfop_row = self.find_cfop(desc, estado)
        ncm_row = self.find_ncm(ncm)

        if not cfop_row:
            raise RuntimeError("CFOP não encontrado para esta natureza/estado.")
        if not ncm_row or not ncm_row.get("ncm"):
            raise RuntimeError("NCM não encontrado na base.")

        ncm_code, cest, cst, aliquota, st = self.get_info(ncm_row)

        return {
            "cfop": cfop_row,   # pode ser dict (repo retorna mappings) ou string
            "ncm": ncm_code,    # não exibido na view, mas mantido no retorno
            "cest": cest if cest else "Sem CEST",
            "cst": cst,
            "aliquota": aliquota,
            "subs_trib": "SIM" if st else "NÃO"
        }

    def get_info(self, ncm_row):
        ncm_code = ncm_row.get("ncm")
        cest = ncm_row.get("cest")
        cst = ncm_row.get("cst")
        aliquota = ncm_row.get("aliquota")
        st = ncm_row.get("st")
        return ncm_code, cest, cst, aliquota, st
