
const API_URL = 'http://localhost:8000';

export const obrasServiceSafe = {
    test: () => console.log("Service Safe Works"),

    getItemsByObra: async (obraId: string): Promise<any[]> => {
        try {
            const response = await fetch(`${API_URL}/construction/obras/${obraId}/items`);
            if (!response.ok) {
                // Return empty array on failure to prevent app crash
                console.error('Failed to fetch items');
                return [];
            }
            return response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            return [];
        }
    }
};
