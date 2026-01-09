
import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { CircleDollarSign, Building2, Package, FileText, ArrowUpRight } from 'lucide-react';

// --- INLINED MOCK DATA (To avoid strict import issues) ---

interface Obra {
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

const mockObras: Obra[] = [
    {
        id: "1",
        nome: "CONDOMÍNIO - SQSW 504",
        dataInicio: "2025-09-01",
        valorContrato: 308951.54,
        condicaoPagamento: "Venda Futura",
        valorAFaturar: 308951.54,
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
        valorFaturado: 366915.82,
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

const mockNotasFiscais = [
    { numero: "1352139", data: "2025-02-01", valorTotal: 2081.04 },
    { numero: "1352140", data: "2025-02-01", valorTotal: 3090.40 }
];

const mockMateriaisSantaLuzia = [
    { nome: 'Alumínio', valorTotal: 8154.60 + 2535.40, tipo: 'ALUMINIO' },
    { nome: 'Acessórios', valorTotal: 1200.00, tipo: 'ACESSORIO' } // Mocked value
];

// ---------------------------------------------------------

const COLORS = ['#0F766E', '#F59E0B', '#EF4444', '#3B82F6'];

export function DashboardObras() {
    const [obras, setObras] = useState<Obra[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate API call
        setTimeout(() => {
            setObras(mockObras);
            setLoading(false);
        }, 800);
    }, []);

    // Aggregations
    const totalContratos = obras.reduce((acc, curr) => acc + curr.valorContrato, 0);
    const totalFaturado = obras.reduce((acc, curr) => acc + curr.valorFaturado, 0);
    const totalAFaturar = obras.reduce((acc, curr) => acc + curr.valorAFaturar, 0);

    // Chart Data Preparation
    const obrasChartData = obras.map(o => ({
        name: o.nome.length > 15 ? o.nome.substring(0, 12) + '...' : o.nome,
        Faturado: o.valorFaturado,
        Restante: o.valorAFaturar,
    }));

    const materiaisChartData = [
        { name: 'Alumínio', value: mockMateriaisSantaLuzia.filter(m => m.tipo === 'ALUMINIO').reduce((acc, curr) => acc + curr.valorTotal, 0) },
        { name: 'Acessórios', value: mockMateriaisSantaLuzia.filter(m => m.tipo === 'ACESSORIO').reduce((acc, curr) => acc + curr.valorTotal, 0) }
    ];

    if (loading) return (
        <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
        </div>
    );

    return (
        <div className="min-h-screen p-8 bg-slate-50 dark:bg-slate-900 space-y-8 font-sans">
            <header className="mb-8">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-800 to-teal-600 bg-clip-text text-transparent flex items-center gap-2">
                    <Building2 className="text-emerald-600" />
                    Dashboard Financeiro de Obras
                </h1>
                <p className="text-slate-500 dark:text-slate-400">Visão consolidada de contratos e materiais</p>
            </header>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KpiCard
                    title="Valor Total Contratos"
                    value={formatCurrency(totalContratos)}
                    icon={<Building2 className="text-emerald-600" />}
                    trend="+12%"
                    trendUp={true}
                />
                <KpiCard
                    title="Total Faturado"
                    value={formatCurrency(totalFaturado)}
                    icon={<CircleDollarSign className="text-teal-600" />}
                    trend={`Total: ${(totalFaturado / totalContratos * 100).toFixed(1)}%`}
                    trendUp={true}
                />
                <KpiCard
                    title="A Faturar"
                    value={formatCurrency(totalAFaturar)}
                    icon={<ArrowUpRight className="text-amber-500" />}
                    trend="Pendente"
                    trendUp={false}
                />
                <KpiCard
                    title="Notas Fiscais (Mês)"
                    value={mockNotasFiscais.length.toString()}
                    icon={<FileText className="text-blue-500" />}
                    trend="Novos registros"
                    trendUp={true}
                />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Bar Chart: Progress by Project */}
                <div className="glass-card p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
                    <h3 className="text-lg font-semibold mb-6 text-slate-800 dark:text-slate-100 flex items-center gap-2">
                        <Building2 className="w-5 h-5 text-emerald-500" />
                        Faturamento por Obra
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={obrasChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis
                                    stroke="#64748b"
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(value) => `R$${(value / 1000).toFixed(0)}k`}
                                />
                                <Tooltip
                                    cursor={{ fill: '#f1f5f9' }}
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Legend />
                                <Bar dataKey="Faturado" fill="#0F766E" radius={[4, 4, 0, 0]} stackId="a" />
                                <Bar dataKey="Restante" fill="#cbd5e1" radius={[4, 4, 0, 0]} stackId="a" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Pie Chart: Materials Distribution */}
                <div className="glass-card p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
                    <h3 className="text-lg font-semibold mb-6 text-slate-800 dark:text-slate-100 flex items-center gap-2">
                        <Package className="w-5 h-5 text-teal-500" />
                        Distribuição de Materiais
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={materiaisChartData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {materiaisChartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Detailed Table Section */}
            <div className="glass-card rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
                <div className="p-6 border-b border-slate-100 dark:border-slate-700">
                    <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Detalhamento de Obras</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 font-semibold uppercase">
                            <tr>
                                <th className="px-6 py-4">Obra</th>
                                <th className="px-6 py-4">Data Início</th>
                                <th className="px-6 py-4">Status Doc</th>
                                <th className="px-6 py-4 text-right">Valor Contrato</th>
                                <th className="px-6 py-4 text-right">Faturado</th>
                                <th className="px-6 py-4 text-right">Progresso</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                            {obras.map((obra) => {
                                const percentual = obra.valorContrato > 0
                                    ? (obra.valorFaturado / obra.valorContrato) * 100
                                    : 0;

                                return (
                                    <tr key={obra.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30 transition-colors">
                                        <td className="px-6 py-4 font-medium text-slate-900 dark:text-slate-100">{obra.nome}</td>
                                        <td className="px-6 py-4 text-slate-500">{new Date(obra.dataInicio).toLocaleDateString('pt-BR')}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${obra.checkListDocumentos
                                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
                                                    : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
                                                }`}>
                                                {obra.checkListDocumentos ? 'Completo' : 'Pendente'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right font-medium text-slate-900 dark:text-slate-100">
                                            {formatCurrency(obra.valorContrato)}
                                        </td>
                                        <td className="px-6 py-4 text-right text-emerald-600 font-medium">
                                            {formatCurrency(obra.valorFaturado)}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <span className="text-xs text-slate-500">{percentual.toFixed(1)}%</span>
                                                <div className="w-16 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${percentual}%` }}></div>
                                                </div>
                                            </div>
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

function KpiCard({ title, value, icon, trend, trendUp }: any) {
    return (
        <div className="glass-card p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
                <span className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    {icon}
                </span>
                {trend && (
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${trendUp
                            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                            : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'
                        }`}>
                        {trend}
                    </span>
                )}
            </div>
            <h3 className="text-slate-500 dark:text-slate-400 text-sm font-medium">{title}</h3>
            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{value}</p>
        </div>
    );
}

function formatCurrency(value: number) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}
