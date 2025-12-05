<script lang="ts">
    import { onMount } from "svelte";
    import { fetchDocuments, type Document } from "$lib/api";
    import DocumentUpload from "$lib/components/DocumentUpload.svelte";

    let documents: Document[] = [];
    let loading = true;
    let error: string | null = null;

    async function loadDocuments() {
        loading = true;
        error = null;
        try {
            documents = await fetchDocuments();
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        loadDocuments();
    });
</script>

<div class="page">
    <div class="header">
        <h1>Documents</h1>
    </div>

    <DocumentUpload on:uploadComplete={loadDocuments} />

    {#if loading}
        <p>Loading documents...</p>
    {:else if error}
        <div class="error">{error}</div>
    {:else if documents.length === 0}
        <div class="empty-state">
            <p>No documents found. Upload one to get started.</p>
        </div>
    {:else}
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Format</th>
                    <th>Date</th>
                    <th>Pages</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {#each documents as doc}
                    <tr>
                        <td>
                            <div class="doc-title">{doc.title}</div>
                            <div class="doc-uri">{doc.uri}</div>
                        </td>
                        <td>{doc.format || "unknown"}</td>
                        <td
                            >{doc.upload_date
                                ? new Date(doc.upload_date).toLocaleDateString()
                                : "-"}</td
                        >
                        <td>{doc.page_count || "-"}</td>
                        <td>
                            <a
                                href="/validation?doc_id={doc.id}"
                                class="action-btn"
                            >
                                Validate Rules
                            </a>
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
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background: rgba(30, 30, 45, 0.5);
        border-radius: 8px;
        overflow: hidden;
    }

    th {
        text-align: left;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.2);
        color: #aaa;
        font-weight: 500;
    }

    td {
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    tr:last-child td {
        border-bottom: none;
    }

    .doc-title {
        color: white;
        font-weight: 500;
    }

    .doc-uri {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.25rem;
    }

    .action-btn {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border-radius: 4px;
        text-decoration: none;
        font-size: 0.9rem;
        transition: background 0.2s;
    }

    .action-btn:hover {
        background: rgba(59, 130, 246, 0.3);
    }

    .error {
        color: #f87171;
        padding: 1rem;
        background: rgba(248, 113, 113, 0.1);
        border-radius: 4px;
    }

    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
</style>
