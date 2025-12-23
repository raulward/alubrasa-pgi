
import { useState, useEffect } from 'react';
import { itemsServiceSafe } from './itemsServiceSafe';

interface LocalItem {
    id: string;
    codigo: string;
    descricao: string;
    unidade: string;
    quantidade: number;
    peso: number;
}

export default function ItemsPage() {
    const [items, setItems] = useState<LocalItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        // Using Demo Obra ID
        itemsServiceSafe.listItems("550e8400-e29b-41d4-a716-446655440000")
            .then(data => {
                console.log("Fetched Items:", data);
                setItems(data || []);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-bold">Informações NF (Itens) - Safe Mode</h1>
            <p className="text-gray-500">Funcionalidade restaurada em modo seguro.</p>

            <div className="border rounded bg-white shadow overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-100 text-gray-700 font-medium border-b">
                        <tr>
                            <th className="px-4 py-3">Código</th>
                            <th className="px-4 py-3">Descrição</th>
                            <th className="px-4 py-3">Unidade</th>
                            <th className="px-4 py-3 text-right">Quantidade</th>
                            <th className="px-4 py-3 text-right">Peso (kg)</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {loading && (
                            <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Carregando...</td></tr>
                        )}
                        {!loading && items.length === 0 && (
                            <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Nenhum item encontrado.</td></tr>
                        )}
                        {!loading && items.map((item, idx) => (
                            <tr key={item.id || idx} className="hover:bg-gray-50">
                                <td className="px-4 py-3 font-medium">{item.codigo}</td>
                                <td className="px-4 py-3">{item.descricao}</td>
                                <td className="px-4 py-3">{item.unidade}</td>
                                <td className="px-4 py-3 text-right">{item.quantidade}</td>
                                <td className="px-4 py-3 text-right">{item.peso}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
