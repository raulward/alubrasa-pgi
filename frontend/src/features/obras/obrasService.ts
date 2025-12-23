
import type { ItemPlanejado, CreateItemDTO, EntregaRealizada, CreateEntregaDTO } from './types';

const API_URL = 'http://localhost:8000'; // Ensure this matches your backend URL

export const obrasService = {
    // Fetch items for a specific Obra (using a hardcoded Obra ID for now if user hasn't created query for Obras yet)
    getItemsByObra: async (obraId: string): Promise<ItemPlanejado[]> => {
        const response = await fetch(`${API_URL}/construction/obras/${obraId}/items`);
        if (!response.ok) {
            throw new Error('Failed to fetch items');
        }
        return response.json();
    },

    createItem: async (item: CreateItemDTO): Promise<ItemPlanejado> => {
        const response = await fetch(`${API_URL}/construction/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(item),
        });
        if (!response.ok) {
            throw new Error('Failed to create item');
        }
        return response.json();
    },

    registerDelivery: async (delivery: CreateEntregaDTO): Promise<EntregaRealizada> => {
        const response = await fetch(`${API_URL}/construction/deliveries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(delivery),
        });
        if (!response.ok) {
            throw new Error('Failed to register delivery');
        }
        return response.json();
    }
};
