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
    source: string;  // 'default' | 'custom' | 'dynamic'
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
/**
 * Document interfaces
 */
export interface Document {
    id: string;
    uri: string;
    title: string;
    format: string | null;
    upload_date: string | null;
    page_count: number | null;
}

export interface PendingRule {
    rule_id: string;
    description: string;
    sparql_pattern: string;
    confidence: number;
    source_doc_uri?: string;
    source_page?: number;
}

/**
 * Fetch list of documents.
 */
export async function fetchDocuments(): Promise<Document[]> {
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) {
        throw new Error(`Failed to fetch documents: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Upload a document.
 */
export async function uploadDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to upload document: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch pending rules.
 */
export async function fetchPendingRules(docId?: string): Promise<PendingRule[]> {
    const params = new URLSearchParams();
    if (docId) params.append('doc_id', docId);

    const response = await fetch(`${API_BASE_URL}/rules/pending?${params}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch pending rules: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Bulk approve rules.
 */
export async function bulkApproveRules(ruleIds: string[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/rules/bulk-approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rule_ids: ruleIds })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to approve rules: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Bulk reject rules.
 */
export async function bulkRejectRules(ruleIds: string[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/rules/bulk-reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rule_ids: ruleIds })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to reject rules: ${response.statusText}`);
    }
    return response.json();
}
