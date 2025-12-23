
import type { PricingInput, PricingOutput } from "./types";

const API_URL = "http://localhost:8000";

export async function calculatePrice(data: PricingInput): Promise<PricingOutput> {
    const response = await fetch(`${API_URL}/pricing/calculate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Erro ao calcular precificação");
    }

    return response.json();
}
