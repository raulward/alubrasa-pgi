
import type { Item, ImportResult } from "./types";

const API_URL = "http://localhost:8000";

export const listItems = async (id_obra: string): Promise<Item[]> => {
    const res = await fetch(`${API_URL}/items/?id_obra=${id_obra}`);
    if (!res.ok) {
        throw new Error("Failed to fetch items");
    }
    return res.json();
};

export const importItems = async (id_obra: string, file: File): Promise<ImportResult> => {
    const formData = new FormData();
    formData.append("id_obra", id_obra);
    formData.append("file", file);

    const res = await fetch(`${API_URL}/items/import`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to import items");
    }
    return res.json();
};
