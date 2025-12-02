/**
 * API client for the SmartMemory Supervision API.
 * Provides functions to interact with the backend endpoints.
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface SystemStats {
    total_triplets: number;
    inferred_triplet_count: number;
    asserted_triplet_count: number;
    active_rule_count: number;
    inactive_rule_count: number;
}

export interface Fact {
    Subject: string;
    Predicate: string;
    Object: string;
    Provenance: string;
}

export interface FactsResponse {
    total_items: number;
    items: Fact[];
}

export interface InferenceRule {
    id: string;
    description: string;
    sparql_query: string;
    is_active: boolean;
    execution_count: number;
    triples_generated: number;
    validation_error: string | null;
}

export interface InferenceRunResponse {
    status: string;
    message: string;
    triples_inferred: number;
}

/**
 * Fetch system statistics.
 */
export async function fetchStats(): Promise<SystemStats> {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch paginated list of facts.
 */
export async function fetchFacts(
    page: number = 1,
    pageSize: number = 50,
    search?: string,
    origin?: string
): Promise<FactsResponse> {
    const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
    });
    if (search) {
        params.append('search', search);
    }
    if (origin) {
        params.append('origin', origin);
    }

    const response = await fetch(`${API_BASE_URL}/facts?${params}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch facts: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch all inference rules.
 */
export async function fetchRules(): Promise<InferenceRule[]> {
    const response = await fetch(`${API_BASE_URL}/rules`);
    if (!response.ok) {
        throw new Error(`Failed to fetch rules: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Toggle a rule's active state.
 */
export async function toggleRule(ruleId: string): Promise<InferenceRule> {
    const response = await fetch(`${API_BASE_URL}/rules/${ruleId}/toggle`, {
        method: 'POST'
    });
    if (!response.ok) {
        throw new Error(`Failed to toggle rule: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Manually trigger an inference run.
 */
export async function runInference(): Promise<InferenceRunResponse> {
    const response = await fetch(`${API_BASE_URL}/inference/run`, {
        method: 'POST'
    });
    if (!response.ok) {
        throw new Error(`Failed to run inference: ${response.statusText}`);
    }
    return response.json();
}
