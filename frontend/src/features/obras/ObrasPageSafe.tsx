
import { useState, useEffect } from 'react';
import { obrasServiceSafe } from './obrasServiceSafe';

// Local Type Definition to avoid importing from types.ts
interface LocalItem {
    id: string;
    codigo_item: string;
    descricao: string | null;
    quantidade_total: number;
    quantidade_entregue: number; // calculated or from API
}

export default function ObrasPage() {
    const [items, setItems] = useState<LocalItem[]>([]);
    const [loading, setLoading] = useState(true);

    useState(() => {
        setLoading(true);
        obrasServiceSafe.getItemsByObra("550e8400-e29b-41d4-a716-446655440000")
            .then(data => {
                console.log("Fetched Items:", data);
                // Map API data to local type if needed, or just cast
                setItems(data || []);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    });

    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-bold">Controle de Obras (Safe Mode)</h1>
            <p className="text-gray-500">Funcionalidade de Obras restaurada em modo seguro.</p>

            <div className="border rounded bg-white shadow overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-100 text-gray-700 font-medium border-b">
                        <tr>
                            <th className="px-4 py-3">Código</th>
                            <th className="px-4 py-3">Descrição</th>
                            <th className="px-4 py-3 text-right">Qtd. Total</th>
                            <th className="px-4 py-3 text-right">Qtd. Entregue</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {loading && (
                            <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">Carregando...</td></tr>
                        )}
                        {!loading && items.length === 0 && (
                            <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">Nenhum item encontrado.</td></tr>
                        )}
                        {!loading && items.map((item, idx) => (
                            <tr key={item.id || idx} className="hover:bg-gray-50">
                                <td className="px-4 py-3 font-medium">{item.codigo_item}</td>
                                <td className="px-4 py-3">{item.descricao}</td>
                                <td className="px-4 py-3 text-right">{item.quantidade_total}</td>
                                <td className="px-4 py-3 text-right">{item.quantidade_entregue || 0}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
