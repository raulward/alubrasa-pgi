
// Mock data generated from Excel files inspection
// Files: "OBRAS_EM_ANDAMENTO.xlsx" and "Controle de Materiais e Notas - SANTA LUZIA III.xlsx"

export interface Obra {
    id: string;
    nome: string;
    dataInicio: string;
    valorContrato: number;
    condicaoPagamento: string;
    valorAFaturar: number;
    valorFaturado: number;
    checkListDocumentos: boolean;
    observacao: string;
}

export const mockObras: Obra[] = [
    {
        id: "1",
        nome: "CONDOMÍNIO - SQSW 504",
        dataInicio: "2025-09-01",
        valorContrato: 308951.54,
        condicaoPagamento: "Venda Futura",
        valorAFaturar: 308951.54, // Deduced
        valorFaturado: 0,
        checkListDocumentos: false,
        observacao: ""
    },
    {
        id: "2",
        nome: "DF STAR - SANTA LUZIA",
        dataInicio: "2025-10-01",
        valorContrato: 1405684.75,
        condicaoPagamento: "28 dias",
        valorAFaturar: 1038768.93,
        valorFaturado: 366915.82, // Deduced
        checkListDocumentos: true,
        observacao: ""
    },
    {
        id: "3",
        nome: "FIRENZE PARK SUL",
        dataInicio: "2024-07-01",
        valorContrato: 2250000.00,
        condicaoPagamento: "",
        valorAFaturar: 2250000.00,
        valorFaturado: 0,
        checkListDocumentos: true,
        observacao: ""
    }
];

export interface ItemMaterial {
    grupo: string;
    codigo: string;
    descricao: string;
    unidade: string;
    cor: string;
    quantidadeTotal: number;
    quantidadeEntregue: number;
    aEntregar: number;
    valorVenda: number;
    valorTotal: number;
    tipo: "ALUMINIO" | "ACESSORIO";
}

export const mockMateriaisSantaLuzia: ItemMaterial[] = [
    // Acessórios
    {
        grupo: "ACESSORIOS",
        codigo: "538303",
        descricao: "CALÇO PARA TRAVAMENTO DO VIDRO 100 X 12 X 3 VERMELHO",
        unidade: "PC",
        cor: "VERMELHO",
        quantidadeTotal: 42,
        quantidadeEntregue: 0,
        aEntregar: 42,
        valorVenda: 0,
        valorTotal: 0,
        tipo: "ACESSORIO"
    },
    // Perfis
    {
        grupo: "PERFIL",
        codigo: "MT-000321",
        descricao: "PERFIL TUBULAR", // Mock description since original was empty
        unidade: "BR",
        cor: "-",
        quantidadeTotal: 157,
        quantidadeEntregue: 127,
        aEntregar: 30,
        valorVenda: 64.21,
        valorTotal: 8154.60,
        tipo: "ALUMINIO"
    },
    {
        grupo: "PERFIL",
        codigo: "MT-000319",
        descricao: "PERFIL ENCAIXE", // Mock description
        unidade: "BR",
        cor: "-",
        quantidadeTotal: 73,
        quantidadeEntregue: 50,
        aEntregar: 23,
        valorVenda: 50.71,
        valorTotal: 2535.40,
        tipo: "ALUMINIO"
    }
];

export interface NotaFiscal {
    numero: string;
    data: string;
    valorTotal: number;
    remessaPara: string;
    codigoPerfil: string;
}

export const mockNotasFiscais: NotaFiscal[] = [
    {
        numero: "1352139",
        data: "2025-02-01",
        valorTotal: 2081.04,
        remessaPara: "ACPA",
        codigoPerfil: "6181058"
    },
    {
        numero: "1352140",
        data: "2025-02-01",
        valorTotal: 3090.40,
        remessaPara: "ACPA",
        codigoPerfil: "6146971"
    }
];
