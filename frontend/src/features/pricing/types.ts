
export interface PricingInput {
    custo_base: number;
    margem_custo_fixo: number;
    margem_lucro_bruto: number;
    ncm: string;
    uf_destino: string;
}

export interface MemoriaItem {
    etapa: string;
    aliquota: string;
    delta_valor: number;
    total_acumulado: number;
}

export interface PricingOutput {
    preco_final: number;
    memoria_calculo: MemoriaItem[];
}
