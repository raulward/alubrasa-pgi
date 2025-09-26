from __future__ import annotations
from core.db_connection import Database, get_db
from utils.validators import Validator

class MapeamentoNFSRepository:

    def __init__(self, db: Database):
        self.__db = db
        self.__validator = Validator()

    def list_descricoes(self):
        db = get_db()
        sql = """
        SELECT descricao
        FROM ref.cfop_map
        WHERE descricao IS NOT NULL
        ORDER BY descricao
        """
        return db.fetch_all(sql)

    def list_estados(self):
        db = get_db()
        sql = """
        SELECT estado
        FROM ref.cfop_map
        WHERE estado IS NOT NULL
        ORDER BY estado
        """
        return db.fetch_all(sql)

    def list_ncms(self):
        db = get_db()
        sql = """
        SELECT ncm
        FROM ref.ncm_map
        WHERE ncm IS NOT NULL
        ORDER BY ncm
        """
        return db.fetch_all(sql)

    def find_cfop(self, descricao: str, estado: str):
        db = get_db()
        sql = """
        SELECT cfop, descricao, operacao, estado
        FROM ref.cfop_map
        WHERE TRIM(LOWER(descricao)) = TRIM(LOWER(:descricao))
          AND TRIM(estado)    = TRIM(:estado)
        LIMIT 1
        """
        return db.fetch_one(sql, {"descricao": descricao, "estado": estado})

    def find_ncm(self, ncm: str):
        db = get_db()
        sql = """
        SELECT ncm, st, cest, cst, aliquota, convenio
        FROM ref.ncm_map
        WHERE ncm = :ncm
        LIMIT 1
        """
        return db.fetch_one(sql, locals())
