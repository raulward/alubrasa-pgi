
from pydantic import BaseModel, Field, field_validator
from typing import List

# --- Models de Saída (Response) ---

class MemoriaItem(BaseModel):
    etapa: str = Field(description="Nome da etapa do cálculo")
    aliquota: str = Field(description="Texto formatado da alíquota (ex: '12.00%')")
    delta: float = Field(alias="delta_valor", description="Valor adicionado ou subtraído nesta etapa")
    total: float = Field(alias="total_acumulado", description="Valor total após esta etapa")

    class Config:
        populate_by_name = True

class PricingOutput(BaseModel):
    preco_final: float
    memoria_calculo: List[MemoriaItem]

    class Config:
        from_attributes = True

# --- Models de Entrada (Request) ---

class PricingInput(BaseModel):
    custo_base: float = Field(..., gt=0, description="Custo base do produto/item")
    margem_custo_fixo: float = Field(..., ge=0, description="Margem de contribuição (Custo Fixo) em %")
    margem_lucro_bruto: float = Field(..., ge=0, description="Margem de lucro bruta pretendida em %")
    ncm: str = Field(..., min_length=4, description="Código NCM (apenas números ou formatado)")
    uf_destino: str = Field(..., min_length=2, max_length=2, description="Sigla da UF de destino (ex: MG)")

    @field_validator('uf_destino')
    def validate_uf(cls, v):
        return v.upper()

    @field_validator('ncm')
    def clean_ncm(cls, v):
        # Remove non-digits to ensure clean usage
        return ''.join(filter(str.isdigit, v))
