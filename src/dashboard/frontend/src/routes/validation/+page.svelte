<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import {
        fetchPendingRules,
        bulkApproveRules,
        bulkRejectRules,
        type PendingRule,
    } from "$lib/api";

    let rules: PendingRule[] = [];
    let loading = true;
    let error: string | null = null;
    let selectedRules: Set<string> = new Set();
    let processing = false;

    $: docIdFilter = $page.url.searchParams.get("doc_id");

    async function loadRules() {
        loading = true;
        error = null;
        try {
            rules = await fetchPendingRules(docIdFilter || undefined);
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    function toggleSelection(ruleId: string) {
        if (selectedRules.has(ruleId)) {
            selectedRules.delete(ruleId);
            selectedRules = selectedRules; // Trigger reactivity
        } else {
            selectedRules.add(ruleId);
            selectedRules = selectedRules;
        }
    }

    function selectAll() {
        if (selectedRules.size === rules.length) {
            selectedRules = new Set();
        } else {
            selectedRules = new Set(rules.map((r) => r.id));
        }
    }

    async function handleBulkApprove() {
        if (selectedRules.size === 0) return;
        processing = true;
        try {
            await bulkApproveRules(Array.from(selectedRules));
            selectedRules = new Set();
            await loadRules();
        } catch (e: any) {
            error = e.message;
        } finally {
            processing = false;
        }
    }

    async function handleBulkReject() {
        if (selectedRules.size === 0) return;
        // No confirmation needed as per user request

        processing = true;
        try {
            await bulkRejectRules(Array.from(selectedRules));
            selectedRules = new Set();
            await loadRules();
        } catch (e: any) {
            error = e.message;
        } finally {
            processing = false;
        }
    }

    onMount(() => {
        loadRules();
    });
</script>

<div class="page">
    <div class="header">
        <h1>Rule Validation</h1>
        {#if docIdFilter}
            <div class="filter-badge">
                Document: {docIdFilter}
                <a href="/validation" class="clear-filter">×</a>
            </div>
        {/if}
    </div>

    <div class="toolbar">
        <div class="selection-info">
            {selectedRules.size} selected
        </div>
        <div class="actions">
            <button
                class="approve-btn"
                on:click={handleBulkApprove}
                disabled={processing || selectedRules.size === 0}
            >
                Approve Selected
            </button>
            <button
                class="reject-btn"
                on:click={handleBulkReject}
                disabled={processing || selectedRules.size === 0}
            >
                Reject Selected
            </button>
        </div>
    </div>

    {#if loading}
        <p>Loading pending rules...</p>
    {:else if error}
        <div class="error">{error}</div>
    {:else if rules.length === 0}
        <div class="empty-state">
            <p>No new rules to validate.</p>
            {#if docIdFilter}
                <p>Try clearing the document filter.</p>
            {/if}
        </div>
    {:else}
        <table>
            <thead>
                <tr>
                    <th class="checkbox-col">
                        <input
                            type="checkbox"
                            checked={selectedRules.size === rules.length &&
                                rules.length > 0}
                            on:change={selectAll}
                            disabled={processing}
                        />
                    </th>
                    <th class="id-col-header">Rule ID</th>
                    <th>Description & Logic</th>
                    <th class="confidence-col-header">Confidence</th>
                    <th class="source-col-header">Source Page</th>
                    <th class="actions-col-header">Actions</th>
                </tr>
            </thead>
            <tbody>
                {#each rules as rule}
                    <tr class:selected={selectedRules.has(rule.id)}>
                        <td class="checkbox-col">
                            <input
                                type="checkbox"
                                checked={selectedRules.has(rule.id)}
                                on:change={() => toggleSelection(rule.id)}
                                disabled={processing}
                            />
                        </td>
                        <td class="id-col">{rule.id}</td>
                        <td>
                            <div class="description">{rule.description}</div>
                            <div class="sparql">{rule.sparql_pattern}</div>
                        </td>
                        <td>
                            <span
                                class="confidence"
                                class:high={rule.confidence > 0.8}
                                class:low={rule.confidence < 0.5}
                            >
                                {Math.round(rule.confidence * 100)}%
                            </span>
                        </td>
                        <td>{rule.source_page || "-"}</td>
                        <td class="actions-col">
                            <button
                                class="icon-btn approve"
                                title="Approve"
                                on:click={() => {
                                    selectedRules.clear();
                                    selectedRules.add(rule.id);
                                    handleBulkApprove();
                                }}
                                disabled={processing}
                            >
                                ✓
                            </button>
                            <button
                                class="icon-btn reject"
                                title="Reject"
                                on:click={() => {
                                    selectedRules.clear();
                                    selectedRules.add(rule.id);
                                    handleBulkReject();
                                }}
                                disabled={processing}
                            >
                                ✗
                            </button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {/if}
</div>

<style>
    .page {
        padding: 2rem;
    }
    .header {
        margin-bottom: 2rem;
    }
    h1 {
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin-bottom: 0.5rem;
    }

    .filter-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    .clear-filter {
        margin-left: 0.5rem;
        cursor: pointer;
        text-decoration: none;
        color: inherit;
        font-weight: bold;
    }

    .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(30, 30, 45, 0.8);
        padding: 1rem;
        border-radius: 8px 8px 0 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: none;
    }

    .actions button {
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        margin-left: 0.5rem;
        font-weight: 500;
    }
    .actions button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .approve-btn {
        background: #10b981;
        color: white;
    }
    .reject-btn {
        background: #ef4444;
        color: white;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(30, 30, 45, 0.5);
        border-radius: 0 0 8px 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        table-layout: fixed;
    }

    th,
    td {
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    th {
        background: rgba(0, 0, 0, 0.2);
        color: #aaa;
        font-weight: 500;
    }
    .checkbox-col {
        width: 40px;
        text-align: center;
    }
    .id-col-header {
        width: 120px;
    }
    .confidence-col-header {
        width: 100px;
    }
    .source-col-header {
        width: 100px;
    }
    .actions-col-header {
        width: 100px;
    }

    /* Description column takes remaining space by default */

    tr.selected {
        background: rgba(59, 130, 246, 0.1);
    }
    /* Rest of CSS... */
    tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    tr.selected:hover {
        background: rgba(59, 130, 246, 0.15);
    }

    .id-col {
        font-family: monospace;
        color: #a5b4fc;
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .description {
        color: white;
        margin-bottom: 0.25rem;
    }
    .sparql {
        font-family: monospace;
        font-size: 0.8rem;
        color: #666;
        background: rgba(0, 0, 0, 0.2);
        padding: 0.25rem;
        border-radius: 3px;
    }

    .confidence {
        font-weight: bold;
        color: #fbbf24;
    }
    .confidence.high {
        color: #4ade80;
    }
    .confidence.low {
        color: #f87171;
    }

    .empty-state {
        text-align: center;
        padding: 4rem;
        color: #666;
        background: rgba(30, 30, 45, 0.5);
        border-radius: 8px;
    }
    .error {
        color: #f87171;
        background: rgba(248, 113, 113, 0.1);
        padding: 1rem;
        border-radius: 8px;
    }

    .icon-btn {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-left: 0.25rem;
    }
    .icon-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .icon-btn.approve {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
    }
    .icon-btn.approve:hover:not(:disabled) {
        background: rgba(16, 185, 129, 0.2);
    }
    .icon-btn.reject {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
    }
    .icon-btn.reject:hover:not(:disabled) {
        background: rgba(239, 68, 68, 0.2);
    }
    .actions-col {
        white-space: nowrap;
    }
</style>
