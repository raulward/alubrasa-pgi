
const API_URL = "http://localhost:8000";

export const itemsServiceSafe = {
    test: () => console.log("Items Service Safe Works"),

    listItems: async (id_obra: string): Promise<any[]> => {
        try {
            const res = await fetch(`${API_URL}/items/?id_obra=${id_obra}`);
            if (!res.ok) {
                console.error("Failed to fetch items");
                return [];
            }
            return res.json();
        } catch (error) {
            console.error("Fetch error:", error);
            return [];
        }
    }
};
