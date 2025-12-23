
import { useState, useEffect } from 'react';
// Minimal imports, no UI components for now to ensure stability
// import { obrasService } from './obrasService';
import { ItemPlanejado } from './types';

export default function ObrasPage() {
    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-bold">Controle de Obras (Safe Mode)</h1>
            <p className="text-gray-500">Funcionalidade simplificada para estabilidade.</p>
            <div className="border p-4 rounded bg-white shadow">
                <p>Obras carregadas aqui...</p>
            </div>
        </div>
    );
}
