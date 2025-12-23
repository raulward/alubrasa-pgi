
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { calculatePrice } from './pricingService';
import type { PricingInput, PricingOutput } from './types';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "../../components/ui/table"

export default function PricingPage() {
    const { register, handleSubmit, formState: { errors } } = useForm<PricingInput>({
        defaultValues: {
            custo_base: 100,
            margem_custo_fixo: 20,
            margem_lucro_bruto: 15,
            ncm: '76042100',
            uf_destino: 'MG'
        }
    });

    const [result, setResult] = useState<PricingOutput | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const onSubmit = async (data: PricingInput) => {
        setLoading(true);
        setError(null);
        try {
            // Ensure numbers are numbers
            const payload = {
                ...data,
                custo_base: Number(data.custo_base),
                margem_custo_fixo: Number(data.margem_custo_fixo),
                margem_lucro_bruto: Number(data.margem_lucro_bruto),
            };
            const res = await calculatePrice(payload);
            setResult(res);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-8 max-w-4xl space-y-8">
            <h1 className="text-3xl font-bold mb-4">Calculadora de Precificação</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <Card>
                    <CardHeader>
                        <CardTitle>Parâmetros de Entrada</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="custo_base">Custo Base (R$)</Label>
                                <Input id="custo_base" type="number" step="0.01" {...register("custo_base", { required: true, min: 0 })} />
                                {errors.custo_base && <span className="text-red-500 text-sm">Campo obrigatório</span>}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="margem_custo_fixo">Margem Custo Fixo (%)</Label>
                                <Input id="margem_custo_fixo" type="number" step="0.1" {...register("margem_custo_fixo", { required: true })} />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="margem_lucro_bruto">Margem Lucro Bruto (%)</Label>
                                <Input id="margem_lucro_bruto" type="number" step="0.1" {...register("margem_lucro_bruto", { required: true })} />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="ncm">NCM</Label>
                                <Input id="ncm" type="text" {...register("ncm", { required: true })} />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="uf_destino">UF Destino</Label>
                                <Input id="uf_destino" type="text" maxLength={2} {...register("uf_destino", { required: true })} />
                            </div>

                            <Button type="submit" className="w-full" disabled={loading}>
                                {loading ? 'Calculando...' : 'Calcular Preço'}
                            </Button>

                            {error && (
                                <div className="p-4 bg-red-100 text-red-700 rounded-md">
                                    {error}
                                </div>
                            )}
                        </form>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Resultado</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {result ? (
                            <div className="space-y-6">
                                <div className="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                                    <p className="text-sm text-gray-600">Preço Final Sugerido</p>
                                    <p className="text-4xl font-bold text-green-700">
                                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(result.preco_final)}
                                    </p>
                                </div>

                                <div className="rounded-md border">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Etapa</TableHead>
                                                <TableHead className="text-right">Alíquota</TableHead>
                                                <TableHead className="text-right">Valor</TableHead>
                                                <TableHead className="text-right">Total Acumulado</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {result.memoria_calculo.map((linha, idx) => (
                                                <TableRow key={idx}>
                                                    <TableCell className="font-medium">{linha.etapa}</TableCell>
                                                    <TableCell className="text-right">{linha.aliquota}</TableCell>
                                                    <TableCell className="text-right">
                                                        {linha.delta_valor !== 0 ? (
                                                            <span className={linha.delta_valor > 0 ? "text-red-600" : "text-blue-600"}>
                                                                {linha.delta_valor > 0 ? '+' : ''}{linha.delta_valor.toFixed(2)}
                                                            </span>
                                                        ) : '-'}
                                                    </TableCell>
                                                    <TableCell className="text-right font-bold">
                                                        {linha.total_acumulado.toFixed(2)}
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-400">
                                Preencha o formulário para ver o resultado
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
