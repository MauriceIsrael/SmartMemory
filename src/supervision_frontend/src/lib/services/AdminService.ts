/**
 * Admin Service API
 * Handles communication with the backend for admin console features,
 * including inference engine management and filtering.
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface InferenceEngineState {
    enabled: boolean;
    name: string;
    rules_loaded: boolean;
}

export interface InferenceEngines {
    owl_reasoning: InferenceEngineState;
    sparql_rules: InferenceEngineState;
}

/**
 * Fetch the current state of all inference engines
 */
export async function getInferenceEngines(): Promise<InferenceEngines> {
    const response = await fetch(`${API_BASE_URL}/inference-engines`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch inference engines: ${response.statusText}`);
    }

    return await response.json();
}

/**
 * Update the state of a specific inference engine
 * @param engineName - Name of the engine ('owl_reasoning' or 'sparql_rules')
 * @param enabled - Whether the engine should be enabled or disabled
 */
export async function updateInferenceEngine(
    engineName: string,
    enabled: boolean
): Promise<InferenceEngineState> {
    const response = await fetch(`${API_BASE_URL}/inference-engines/${engineName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
    });

    if (!response.ok) {
        throw new Error(`Failed to update inference engine: ${response.statusText}`);
    }

    return await response.json();
}

/**
 * Fetch rules with optional filtering
 * @param source - Optional filter: 'default' for built-in rules, 'dynamic' for loaded rules
 */
export async function getRules(source?: 'default' | 'dynamic'): Promise<any[]> {
    const url = new URL(`${API_BASE_URL}/rules`);
    if (source) {
        url.searchParams.append('source', source);
    }

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch rules: ${response.statusText}`);
    }

    return await response.json();
}

/**
 * Fetch facts with optional filtering
 * @param origin - Optional filter: 'explicit' for stated facts, 'inferred' for derived facts
 */
export async function getFacts(origin?: 'explicit' | 'inferred'): Promise<any[]> {
    const url = new URL(`${API_BASE_URL}/facts`);
    if (origin) {
        url.searchParams.append('origin', origin);
    }

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch facts: ${response.statusText}`);
    }

    return await response.json();
}
