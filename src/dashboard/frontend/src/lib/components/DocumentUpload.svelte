<script lang="ts">
    import { uploadDocument } from "$lib/api";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    let files: FileList;
    let uploading = false;
    let message = "";
    let error = "";

    async function handleUpload() {
        if (!files || files.length === 0) return;

        uploading = true;
        message = "";
        error = "";

        try {
            const result = await uploadDocument(files[0]);
            message = `Uploaded! ${result.rules_extracted} rules extracted.`;
            dispatch("uploadComplete");
        } catch (e: any) {
            error = e.message;
        } finally {
            uploading = false;
        }
    }
</script>

<div class="upload-box">
    <h3>Upload Document</h3>
    <input type="file" bind:files accept=".pdf,.txt,.md" disabled={uploading} />
    <button on:click={handleUpload} disabled={!files || uploading}>
        {uploading ? "Uploading..." : "Upload"}
    </button>

    {#if message}
        <div class="success">{message}</div>
    {/if}
    {#if error}
        <div class="error">{error}</div>
    {/if}
</div>

<style>
    .upload-box {
        background: rgba(30, 30, 45, 0.5);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }

    h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #fff;
    }

    input[type="file"] {
        margin-bottom: 1rem;
        display: block;
        color: #ddd;
    }

    button {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        opacity: 0.9;
        transition: opacity 0.2s;
    }

    button:hover:not(:disabled) {
        opacity: 1;
    }

    button:disabled {
        background: #555;
        cursor: not-allowed;
    }

    .success {
        color: #4ade80;
        margin-top: 1rem;
    }

    .error {
        color: #f87171;
        margin-top: 1rem;
    }
</style>
