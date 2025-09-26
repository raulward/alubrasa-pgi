from __future__ import annotations
from repositories.obras_repository import ObraRepository
from utils.validators import Validator

class ObraService:
    def __init__(self, repository: ObraRepository):
        self.repo = repository
        self.validator = Validator()

    def list_itens(self):
        return self.repo.list_ativas()

    def cadastrar(self, *, id_cliente, nome, endereco, cnpj, codigo):
        errs = []
        if not nome.strip(): errs.append("Informe o nome da obra.")
        if not endereco.strip(): errs.append("Informe o endereço da obra.")
        if not self.validator.is_valid_cnpj(cnpj): errs.append("CNPJ da obra inválido.")
        if not codigo.strip(): errs.append("Informe o código da obra.")
        elif self.repo.exists_by_codigo(codigo.strip()):
            errs.append("Já existe uma obra com este código.")
        if errs:
            raise ValueError("\n".join(errs))
        return self.repo.create(
            id_cliente=id_cliente,
            nome=nome.strip(),
            endereco=endereco.strip(),
            cnpj=self.validator.normalize_cnpj(cnpj),
            codigo=codigo.strip(),
        )
