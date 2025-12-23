
-- Create Table for Obras (Construction Projects)
CREATE TABLE IF NOT EXISTS obras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome TEXT
);

-- Create Table for Items Planejados (Planned Items)
CREATE TABLE IF NOT EXISTS items_planejados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    obra_id UUID NOT NULL REFERENCES obras(id) ON DELETE CASCADE,

    codigo_item TEXT NOT NULL,
    descricao TEXT,
    unidade TEXT,
    grupo TEXT, -- Added for separation (e.g. Linha Suprema, Acessórios)
    cor TEXT,   -- Added for Perfis/Accessories color

    quantidade_total FLOAT NOT NULL DEFAULT 0.0,
    preco_venda_unitario FLOAT NOT NULL DEFAULT 0.0,
    categoria TEXT, -- 'PERFIL', 'COMPONENTE', 'VIDRO'

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Table for Entregas Realizadas (Deliveries)
CREATE TABLE IF NOT EXISTS entregas_realizadas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_planejado_id UUID NOT NULL REFERENCES items_planejados(id) ON DELETE CASCADE,

    numero_nf TEXT,
    data_faturamento DATE NOT NULL,
    quantidade_entregue FLOAT NOT NULL DEFAULT 0.0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_items_planejados_obra_id ON items_planejados(obra_id);
CREATE INDEX IF NOT EXISTS idx_entregas_realizadas_item_id ON entregas_realizadas(item_planejado_id);
