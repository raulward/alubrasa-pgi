from __future__ import annotations
from repositories.cliente_repository import ClienteRepository
from utils.validators import Validator

class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo
        self.validator = Validator()

    def list_clientes(self):
        return self.repo.list_clientes()

    def cadastrar(self, *, nome: str, email: str, cnpj: str, telefone: str, endereco: str) -> dict:
        errs = []
        if not nome.strip():
            errs.append("Informe o nome")
        if not self.validator.is_valid_email(email):
            errs.append("E-mail inválido")
        if not cnpj.strip() or self.validator.is_valid_cnpj(cnpj):
            errs.append("Informe um CPF/CNPJ válido.")
        cnpj_digits = self.validator.only_digits(cnpj)
        if self.repo.exists_by_cnpj(cnpj_digits):
            errs.append("Cliente já existente com este CPF/CNPJ.")
        if not telefone.strip():
            errs.append("Insira um telefone válido.")
        if not endereco.strip():
            errs.append("Informe um endereço válido.")
        if errs:
            raise ValueError("\n".join(errs))
        return self.repo.create(nome=nome.strip(), email=email.strip(), cnpj=cnpj_digits, telefone=telefone.strip(), endereco=endereco.strip())
