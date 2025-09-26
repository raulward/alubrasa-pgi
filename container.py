from __future__ import annotations
import streamlit as st
from core.db_connection import get_db, Database
from repositories.cliente_repository import ClienteRepository
from repositories.obras_repository import ObraRepository
from repositories.mapeamento_nfs_repository import MapeamentoNFSRepository
from repositories.itens_orcados_repository import ItensOrcadosRepository
# from repositories.crtl_orcamento import ControleOrcamentoRepository
# from services.crtl_orcamento import ControleOrcamentoService
from repositories.precificacao_repository import PrecificacaoRepository
from services.precificacao_service import PrecificacaoService
from services.cliente_service import ClienteService
from services.obra_service import ObraService
from services.itens_orcados_service import ItensOrcadosService
from services.mapeamento_nfs_service import MapeamentoNFSService


class AppContainer:
    def __init__(self):
        db: Database = get_db()
        self.cliente_repo = ClienteRepository(db)
        self.cliente_service = ClienteService(self.cliente_repo)
        self.obra_repo = ObraRepository(db)
        self.obra_service = ObraService(self.obra_repo)
        self.itens_orcados_repo = ItensOrcadosRepository(db)
        self.itens_orcados_service = ItensOrcadosService(self.itens_orcados_repo)
        self.mapeamento_nfs_repo = MapeamentoNFSRepository(db)
        self.mapeamento_nfs_service = MapeamentoNFSService(self.mapeamento_nfs_repo)
        self.precificacao_repo = PrecificacaoRepository(db)
        self.precificacao_service = PrecificacaoService(self.precificacao_repo)


@st.cache_resource(show_spinner=False)
def get_container() -> AppContainer:
    return AppContainer()
