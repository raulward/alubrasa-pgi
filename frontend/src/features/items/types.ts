
export interface Item {
    id: string;
    codigo: string;
    descricao: string;
    unidade: string;
    grupo: string;
    dimensoes: string;
    quantidade: number;
    peso: number;
    preco_total: number;
    preco_unit: number;
}

export interface ImportResult {
    total_ok: number;
    errors: Array<{ index: number; codigo: string; erro: string }>;
    validation_errors: Array<{ index: number; codigo: string; erros: string[] }>;
}
