
export interface EntregaRealizada {
    id: string;
    item_planejado_id: string;
    numero_nf: string | null;
    data_faturamento: string;
    quantidade_entregue: number;
}

export interface ItemPlanejado {
    id: string;
    obra_id: string;
    codigo_item: string;
    descricao: string | null;
    unidade: string | null;
    quantidade_total: number;
    preco_venda_unitario: number;
    categoria: 'PERFIL' | 'COMPONENTE' | 'VIDRO' | null;
    entregas: EntregaRealizada[];
}

export interface CreateItemDTO {
    obra_id: string;
    codigo_item: string;
    descricao?: string;
    unidade?: string;
    quantidade_total: number;
    preco_venda_unitario: number;
    categoria?: 'PERFIL' | 'COMPONENTE' | 'VIDRO';
}

export interface CreateEntregaDTO {
    item_planejado_id: string;
    numero_nf?: string;
    data_faturamento: string;
    quantidade_entregue: number;
}
