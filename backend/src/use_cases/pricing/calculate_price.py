
from typing import List, Tuple
from .dtos import CalculationResult, LinhaMemoria
from src.use_cases.ports.repositories import TaxRepositoryInterface, NcmRepositoryInterface

def _round2(x: float) -> float:
    return round(x + 1e-12, 2)

def _pct(x: float) -> str:
    return f"{x*100:.2f}%"

def _gross_up(total: float, taxa: float) -> Tuple[float, float]:
    novo = total / (1 - taxa)
    return (_round2(novo - total), _round2(novo))

def _sum_gross_up(total: float, taxas: List[float]) -> Tuple[float, float]:
    t = sum(taxas)
    novo = total / (1 - t)
    return (_round2(novo - total), _round2(novo))

class CalculatePriceUseCase:
    def __init__(
        self,
        tax_repo: TaxRepositoryInterface,
        ncm_repo: NcmRepositoryInterface
    ):
        self.tax_repo = tax_repo
        self.ncm_repo = ncm_repo

    async def execute(
        self,
        custo_base: float,
        margem_custo_fixo: float,
        margem_lucro_bruto: float,
        ncm: str,
        uf_destino: str
    ) -> CalculationResult:

        # 1. Fetch info
        ncm_info = await self.ncm_repo.find_ncm_info(ncm)

        # Try finding ID by code if direct lookup failed or if we need normalized ID for convenio
        ncm_id = None
        if ncm_info:
            ncm_id = ncm_info.get("id")
        else:
             # Fallback: try finding ID by digits only, then get info?
             # Or just fail? Legacy implicitly searches by code.
             # Legacy FindNCM uses direct match. Legacy FindID uses regex.
             # We will try to get the ID via Regex if direct match failed.
             ncm_id = await self.ncm_repo.find_id_by_ncm_code(ncm)
             if not ncm_id:
                 # Cannot proceed without NCM info normally, but let's see if we can just use defaults?
                 # Legacy: if no NCM info found, fields like 'st' are None -> False.
                 pass

        # If we didn't get ncm_info earlier, but found an ID, maybe we should fetch info by ID?
        # For this refactoring, let's assume if ncm_info is missing, we treat as no ST.

        usa_st = bool(ncm_info.get("st")) if ncm_info else False

        has_convenio = False
        if usa_st and ncm_info and ncm_info.get("convenio") == "sim":
             # We need ncm_id for the convenio check
             if not ncm_id and ncm_info.get("id"):
                 ncm_id = str(ncm_info.get("id"))

             if ncm_id:
                has_convenio = await self.ncm_repo.has_convenio(ncm_id, uf_destino)

        pis_val = await self.tax_repo.get_pis()
        cofins_val = await self.tax_repo.get_cofins() # Warning: Legacy used 'get_confins' alias too

        # Normalize taxes
        pis = pis_val / 100.0 if pis_val > 1 else pis_val
        cofins = cofins_val / 100.0 if cofins_val > 1 else cofins_val

        # Logic from Legacy
        memoria: List[LinhaMemoria] = []
        total = _round2(custo_base)
        memoria.append(LinhaMemoria("Custo com impostos", "", 0.00, total))

        if usa_st:
            # Com ST
            # No legacy: custo_liquido = custo_base
            icms_saida_pct = 0.0 if has_convenio else 0.20
            memoria.append(LinhaMemoria("ST na origem (embutida)", "—", 0.00, total))
            custo_liquido = custo_base
        else:
            # Sem ST
            icms_ent = 0.12
            icms_ent_val = _round2(total * icms_ent)
            pis_ent_val  = _round2(total * pis)
            cof_ent_val  = _round2(total * cofins)
            total_liq    = _round2(total - icms_ent_val - pis_ent_val - cof_ent_val)

            memoria.append(LinhaMemoria("ICMS ENTRADA", _pct(icms_ent), -icms_ent_val, _round2(total - icms_ent_val)))
            memoria.append(LinhaMemoria("PIS ENTRADA",  _pct(pis),      -pis_ent_val,  _round2(total - icms_ent_val - pis_ent_val)))
            memoria.append(LinhaMemoria("COFINS ENTRADA", _pct(cofins), -cof_ent_val,  total_liq))

            total = total_liq
            custo_liquido = total_liq # This needs to match legacy logic flow.
            # In legacy, 'total' inside memoria calculation logic tracks the running total,
            # while 'custo_liquido' is used for the direct formula.
            # The running total 'total' at this point IS custo_liquido.
            icms_saida_pct = 0.13

        # Custo Fixo
        total_cf = _round2(total / (1 - margem_custo_fixo/100.0))
        memoria.append(LinhaMemoria("Margem Cont. Custo Fixo", _pct(margem_custo_fixo/100.0), _round2(total_cf - total), total_cf))
        total = total_cf

        # Margem Lucro
        total_ml = _round2(total / (1 - margem_lucro_bruto/100.0))
        memoria.append(LinhaMemoria("Margem de Lucro Bruta Pretendida", _pct(margem_lucro_bruto/100.0), _round2(total_ml - total), total_ml))
        total = total_ml

        # PIS+COFINS Saida
        delta_pc, total_pc = _sum_gross_up(total, [pis, cofins])
        memoria.append(LinhaMemoria("PIS + COFINS (saída)", _pct(pis + cofins), delta_pc, total_pc))
        total = total_pc

        # ICMS Saida
        if usa_st:
            etiqueta = "ICMS Saída (ST/convênio)" if has_convenio else "ICMS Saída (ST s/ convênio)"
        else:
            etiqueta = "ICMS Saída"

        delta_icms, total_final = _gross_up(total, icms_saida_pct)
        memoria.append(LinhaMemoria(etiqueta, _pct(icms_saida_pct), delta_icms, total_final))

        return CalculationResult(
            preco_final=_round2(total_final),
            memoria_calculo=memoria
        )
