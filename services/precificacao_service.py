from __future__ import annotations
from repositories.precificacao_repository import PrecificacaoRepository
from utils.validators import Validator
from services.mapeamento_nfs_service import MapeamentoNFSService
from collections.abc import Mapping
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class LinhaMemoria:
    etapa: str
    aliquota: str
    delta: float
    total: float

def _pct(x: float) -> str:
    return f"{x*100:.2f}%"

def _round2(x: float) -> float:
    return round(x + 1e-12, 2)

def _gross_up(total: float, taxa: float) -> Tuple[float, float]:
    novo = total / (1 - taxa)
    return (_round2(novo - total), _round2(novo))

def _sum_gross_up(total: float, taxas: List[float]) -> Tuple[float, float]:
    t = sum(taxas)
    novo = total / (1 - t)
    return (_round2(novo - total), _round2(novo))

class PrecificacaoService:
    def __init__(self, repo: PrecificacaoRepository):
        self._repo = repo
        self._validator = Validator()

    def calcular(self, custo_base: float, margem_custo_fixo: float, margem_lucro_bruto: float,
             ncm: str, uf_destino: str):
        mnf = MapeamentoNFSService()
        ncm_info = mnf.find_ncm(ncm)

        usa_st = bool(ncm_info.get("st"))
        has_convenio = (
            usa_st
            and (ncm_info.get("convenio") == "sim")
            and self._repo.find_convenio(ncm_info, uf_destino)   # UF de DESTINO
        )

        pis    = self._to_num(self._repo.get_pis())
        cofins = self._to_num(self._repo.get_cofins())
        # se vierem em %, converte para fração
        if pis > 1:    pis    = pis / 100.0
        if cofins > 1: cofins = cofins / 100.0

        if usa_st:
            # Com ST: não desonera entrada
            custo_liquido = custo_base
            icms_saida_pct = 0.0 if has_convenio else 0.20
        else:
            # Sem ST (Lei 5.005 DF): subtrai ICMS de entrada **e** PIS+COFINS da ENTRADA
            icms_entrada_pct   = 0.12
            pis_cofins_entrada = pis + cofins
            # desonerações de entrada aplicadas ao custo
            custo_liquido = custo_base * (1 - icms_entrada_pct - pis_cofins_entrada)
            icms_saida_pct = 0.13

        # custo fixo → margem → tributos de SAÍDA (PIS/COFINS) → ICMS de saída
        base = custo_liquido / (1 - (margem_custo_fixo / 100))
        base = base / (1 - (margem_lucro_bruto / 100))
        base = base / (1 - (pis + cofins))        # PIS+COFINS de SAÍDA (atenção aos parênteses!)
        preco_final = base / (1 - icms_saida_pct)

        return preco_final



    def list_ufs(self):
        rows = self._repo.list_ufs()  # ex.: [ {'sigla_estado':'AC'}, {'sigla_estado':'AL'}, ... ]
        ufs: list[str] = []
        for r in rows:
            if isinstance(r, Mapping):
                v = r.get("sigla_estado") or r.get("uf") or r.get("sigla")
            else:
                # Row/objeto/tupla
                v = getattr(r, "sigla_estado", None) or getattr(r, "uf", None) or getattr(r, "sigla", None)
                if v is None and isinstance(r, (tuple, list)) and r:
                    v = r[0]
            if v:
                ufs.append(str(v))
        # remove duplicados e ordena
        return sorted(set(ufs))

    def _to_num(self, x) -> float:
        if x is None:
            return 0.0
        if isinstance(x, (int, float)):
            return float(x)
        if isinstance(x, Decimal):
            return float(x)
        if isinstance(x, Mapping):  # Row/Dict do DB
            # tenta a chave 'tx' primeiro, senão o primeiro valor numérico
            if "tx" in x:
                return float(x["tx"])
            for v in x.values():
                try:
                    return float(v)
                except (TypeError, ValueError):
                    continue
            return 0.0
        # fallback
        return float(x)

    def memoria_calculo(
        self,
        *,
        custo_base: float,
        margem_custo_fixo: float,
        margem_lucro_bruto: float,
        ncm: str,
        uf_destino: str
    ) -> List[LinhaMemoria]:
        """
        Gera as linhas da memória de cálculo para:
        - Sem ST
        - Com ST + Convênio
        - Com ST + Sem Convênio
        Usa os mesmos parâmetros do cálculo atual para espelhar a planilha.
        """

        # --- descobrir cenário (usa_st/has_convenio) e taxas ---
        mnf = MapeamentoNFSService()
        ncm_info = mnf.find_ncm(ncm)

        usa_st = bool(ncm_info.get("st"))
        has_convenio = (
            usa_st
            and (ncm_info.get("convenio") == "sim")
            and self._repo.find_convenio(ncm_info, uf_destino)
        )

        pis = self._to_num(self._repo.get_pis())
        cofins = self._to_num(self._repo.get_cofins())
        if pis > 1:    pis    = pis / 100.0
        if cofins > 1: cofins = cofins / 100.0

        linhas: List[LinhaMemoria] = []
        total = _round2(custo_base)
        linhas.append(LinhaMemoria("Custo com impostos", "", 0.00, total))

        # --- entrada ---
        if not usa_st:
            icms_ent = 0.12
            icms_ent_val = _round2(total * icms_ent)
            pis_ent_val  = _round2(total * pis)
            cof_ent_val  = _round2(total * cofins)
            total_liq    = _round2(total - icms_ent_val - pis_ent_val - cof_ent_val)

            linhas += [
                LinhaMemoria("ICMS ENTRADA", _pct(icms_ent),  -icms_ent_val, _round2(total - icms_ent_val)),
                LinhaMemoria("PIS ENTRADA",  _pct(pis),       -pis_ent_val,  _round2(total - icms_ent_val - pis_ent_val)),
                LinhaMemoria("COFINS ENTRADA", _pct(cofins),  -cof_ent_val,  total_liq),
            ]
            total = total_liq
        else:
            linhas.append(LinhaMemoria("ST na origem (embutida)", "—", 0.00, total))

        # --- custo fixo ---
        total_cf = _round2(total / (1 - margem_custo_fixo))
        linhas.append(LinhaMemoria("Margem Cont. Custo Fixo", _pct(margem_custo_fixo), _round2(total_cf - total), total_cf))
        total = total_cf

        # --- margem lucro ---
        total_ml = _round2(total / (1 - margem_lucro_bruto))
        linhas.append(LinhaMemoria("Margem de Lucro Bruta Pretendida", _pct(margem_lucro_bruto), _round2(total_ml - total), total_ml))
        total = total_ml

        # --- PIS+COFINS de saída ---
        delta_pc, total_pc = _sum_gross_up(total, [pis, cofins])
        linhas.append(LinhaMemoria("PIS + COFINS (saída)", _pct(pis + cofins), delta_pc, total_pc))
        total = total_pc

        # --- ICMS de saída ---
        if usa_st:
            icms_sai = 0.0 if has_convenio else 0.20
            etiqueta = "ICMS Saída (ST/convênio)" if has_convenio else "ICMS Saída (ST s/ convênio)"
        else:
            icms_sai = 0.13
            etiqueta = "ICMS Saída"

        delta_icms, total_final = _gross_up(total, icms_sai)
        linhas.append(LinhaMemoria(etiqueta, _pct(icms_sai), delta_icms, total_final))
        return linhas
