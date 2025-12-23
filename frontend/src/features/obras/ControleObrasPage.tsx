
import { useState, useEffect } from 'react';
import { obrasServiceSafe } from './obrasServiceSafe';

// Local Type Definition to avoid import toxicity
interface ConstructionItem {
    id: string;
    grupo: string | null;
    codigo_item: string;
    descricao: string | null;
    unidade: string | null;
    cor: string | null;
    quantidade_total: number;
    quantidade_entregue: number; // mapped from API relations if complex, or direct field
    preco_venda_unitario: number;
    categoria: 'PERFIL' | 'COMPONENTE' | 'VIDRO' | null;
    entregas?: any[];
}

export default function ControleObrasPage() {
    const [items, setItems] = useState<ConstructionItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'perfis' | 'componentes'>('perfis');
    const [error, setError] = useState<string | null>(null);

    // Hardcoded ID for MVP/Testing as in previous steps
    const OBRA_ID = "550e8400-e29b-41d4-a716-446655440000";

    useEffect(() => {
        loadItems();
    }, []);

    const loadItems = async () => {
        setLoading(true);
        try {
            const data = await obrasServiceSafe.getItemsByObra(OBRA_ID);
            // Calculate 'quantidade_entregue' if it comes from relations,
            // but for now assuming it might be on the main object or we sum relations.
            // Adjust based on actual API response structure.
            const processedData = data.map((item: any) => ({
                ...item,
                // Sum deliveries if API returns 'entregas' list, otherwise use field if exists
                quantidade_entregue: item.entregas
                    ? item.entregas.reduce((acc: number, ent: any) => acc + (ent.quantidade_entregue || 0), 0)
                    : (item.quantidade_entregue || 0)
            }));
            setItems(processedData);
            setError(null);
        } catch (err) {
            console.error(err);
            setError("Erro ao carregar itens da obra.");
        } finally {
            setLoading(false);
        }
    };

    const filteredItems = items.filter(item => {
        if (activeTab === 'perfis') return item.categoria === 'PERFIL';
        return item.categoria !== 'PERFIL'; // Componentes, Vidros, etc.
    });

    return (
        <div className="p-6 space-y-6 bg-slate-50 min-h-screen font-sans">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Controle de Obras</h1>
                    <p className="text-slate-500">Gerenciamento de Perfis e Componentes</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={loadItems}
                        className="px-4 py-2 bg-white border border-slate-200 rounded-md text-sm font-medium hover:bg-slate-100 transition shadow-sm"
                    >
                        Atualizar
                    </button>
                    <label className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm font-medium hover:bg-slate-800 transition shadow-sm cursor-pointer">
                        Importar CSV
                        <input
                            type="file"
                            accept=".csv"
                            className="hidden"
                            onChange={async (e) => {
                                if (e.target.files && e.target.files[0]) {
                                    setLoading(true);
                                    try {
                                        await obrasServiceSafe.importItems(OBRA_ID, e.target.files[0]);
                                        await loadItems();
                                        alert('Importação concluída com sucesso!');
                                    } catch (err) {
                                        console.error(err);
                                        alert('Erro ao importar arquivo.');
                                    } finally {
                                        setLoading(false);
                                    }
                                }
                            }}
                        />
                    </label>
                </div>
            </div>

            {/* Manual Tabs */}
            <div className="border-b border-slate-200">
                <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                    <button
                        onClick={() => setActiveTab('perfis')}
                        className={`
                            whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === 'perfis'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
                        `}
                    >
                        Perfis
                    </button>
                    <button
                        onClick={() => setActiveTab('componentes')}
                        className={`
                            whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === 'componentes'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
                        `}
                    >
                        Componentes
                    </button>
                </nav>
            </div>

            {/* Content */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 text-slate-700 font-medium border-b border-slate-200">
                            <tr>
                                <th className="px-4 py-3">Grupo</th>
                                <th className="px-4 py-3">Código</th>
                                <th className="px-4 py-3">Descrição</th>
                                <th className="px-4 py-3">Cor</th>
                                <th className="px-4 py-3">Unidade</th>
                                <th className="px-4 py-3 text-right">Qtd. Total</th>
                                <th className="px-4 py-3 text-right">Qtd. Entregue</th>
                                <th className="px-4 py-3 text-right">Saldo</th>
                                <th className="px-4 py-3 text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading && (
                                <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-500">Carregando itens...</td></tr>
                            )}
                            {error && (
                                <tr><td colSpan={9} className="px-4 py-8 text-center text-red-500">{error}</td></tr>
                            )}
                            {!loading && !error && filteredItems.length === 0 && (
                                <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-500">Nenhum item encontrado nesta categoria.</td></tr>
                            )}
                            {!loading && filteredItems.map((item) => {
                                const saldo = item.quantidade_total - item.quantidade_entregue;
                                return (
                                    <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-4 py-3 text-slate-600">{item.grupo || '-'}</td>
                                        <td className="px-4 py-3 font-medium text-slate-900">{item.codigo_item}</td>
                                        <td className="px-4 py-3 text-slate-600 max-w-xs truncate" title={item.descricao || ''}>{item.descricao}</td>
                                        <td className="px-4 py-3 text-slate-600">{item.cor || '-'}</td>
                                        <td className="px-4 py-3 text-slate-600">{item.unidade || '-'}</td>
                                        <td className="px-4 py-3 text-right font-medium">{item.quantidade_total}</td>
                                        <td className="px-4 py-3 text-right text-green-600">{item.quantidade_entregue}</td>
                                        <td className={`px-4 py-3 text-right font-bold ${saldo > 0 ? 'text-orange-500' : 'text-slate-400'}`}>
                                            {saldo > 0 ? saldo : 'OK'}
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <button
                                                className="text-blue-600 hover:text-blue-800 text-xs font-semibold uppercase tracking-wider border border-blue-200 hover:border-blue-400 px-2 py-1 rounded transition"
                                                onClick={() => console.log('Registrar entrega', item.id)}
                                            >
                                                Entregar
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
