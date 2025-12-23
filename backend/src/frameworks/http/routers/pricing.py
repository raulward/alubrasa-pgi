
from fastapi import APIRouter, Depends, HTTPException
from src.frameworks.http.schemas.pricing import PricingInput, PricingOutput, MemoriaItem
from src.use_cases.pricing.calculate_price import CalculatePriceUseCase
from src.frameworks.http.dependencies import get_pricing_use_case

router = APIRouter(prefix="/pricing", tags=["Precificação"])

@router.post("/calculate", response_model=PricingOutput)
async def calculate_pricing(
    data: PricingInput,
    use_case: CalculatePriceUseCase = Depends(get_pricing_use_case)
):
    try:
        result = await use_case.execute(
            custo_base=data.custo_base,
            margem_custo_fixo=data.margem_custo_fixo,
            margem_lucro_bruto=data.margem_lucro_bruto,
            ncm=data.ncm,
            uf_destino=data.uf_destino
        )

        # Mapping Dataclass -> Pydantic
        # Note: Pydantic Config from_attributes=True handles simple mapping,
        # but we need to map MemoriaItem fields (delta->delta_valor, etc) if using alias.
        # However, the Pydantic model uses aliases. DataClass has 'delta' and 'total'.
        # Pydantic via from_attributes looks up by attribute name 'delta', which matches field name 'delta'.
        # The alias 'delta_valor' is for JSON output. So it should work fine.

        return result
    except Exception as e:
        # In a real app, handle specific domain exceptions nicely
        raise HTTPException(status_code=400, detail=str(e))
