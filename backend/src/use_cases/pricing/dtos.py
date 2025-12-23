
from dataclasses import dataclass
from typing import List

@dataclass
class LinhaMemoria:
    etapa: str
    aliquota: str
    delta: float
    total: float

@dataclass
class CalculationResult:
    preco_final: float
    memoria_calculo: List[LinhaMemoria]
