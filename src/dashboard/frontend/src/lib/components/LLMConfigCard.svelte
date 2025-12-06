<script lang="ts">
    import type { LLMConfig, LLMTestResult } from "$lib/services/AdminService";

    export let llmConfig: LLMConfig;
    export let llmConfigured: boolean;
    export let savingLLM: boolean;
    export let testingLLM: boolean;
    export let llmError: string | null;
    export let llmTestResult: LLMTestResult | null;
    export let onSave: () => Promise<void>;
    export let onTest: () => Promise<void>;

    const providers = [
        { value: "ollama", label: "Ollama (Local)" },
        { value: "openai", label: "OpenAI" },
        { value: "anthropic", label: "Anthropic (Claude)" },
        { value: "google", label: "Google (Gemini)" },
    ];
</script>

<div class="admin-card">
    <h2>
        🤖 LLM Configuration
        {#if llmConfigured}
            <span class="status-badge configured">✓ Configured</span>
        {:else}
            <span class="status-badge not-configured">⚠ Not Configured</span>
        {/if}
    </h2>
    <p class="description">
        Configure the LLM provider for document rule extraction. Required for
        processing uploaded documents.
    </p>

    <div class="config-grid">
        <div class="form-group">
            <label for="provider">Provider:</label>
            <select id="provider" bind:value={llmConfig.provider}>
                {#each providers as { value, label }}
                    <option {value}>{label}</option>
                {/each}
            </select>
        </div>

        {#if llmConfig.provider === "ollama"}
            <div class="form-group">
                <label for="base_url">Base URL:</label>
                <input
                    id="base_url"
                    type="text"
                    bind:value={llmConfig.base_url}
                    placeholder="http://localhost:11434"
                />
            </div>

            <div class="form-group">
                <label for="model">Model:</label>
                <input
                    id="model"
                    type="text"
                    bind:value={llmConfig.model}
                    placeholder="llama3, mistral, etc."
                />
            </div>
        {:else}
            <div class="form-group">
                <label for="api_key">API Key:</label>
                <input
                    id="api_key"
                    type="password"
                    bind:value={llmConfig.api_key}
                    placeholder="sk-..."
                />
            </div>

            <div class="form-group">
                <label for="model">Model:</label>
                <input
                    id="model"
                    type="text"
                    bind:value={llmConfig.model}
                    placeholder="gpt-4, claude-3-5-sonnet, etc."
                />
            </div>
        {/if}

        <div class="form-group">
            <label for="temperature">Temperature:</label>
            <input
                id="temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                bind:value={llmConfig.temperature}
            />
        </div>
    </div>

    <div class="action-buttons">
        <button on:click={onTest} disabled={testingLLM} class="test-button">
            {testingLLM ? "Testing..." : "🧪 Test Connection"}
        </button>
        <button on:click={onSave} disabled={savingLLM} class="save-button">
            {savingLLM ? "Saving..." : "💾 Save Configuration"}
        </button>
    </div>

    {#if llmError}
        <div class="result-box error">
            <h3>❌ Error</h3>
            <p>{llmError}</p>
        </div>
    {/if}

    {#if llmTestResult}
        <div
            class="result-box"
            class:success={llmTestResult.success}
            class:error={!llmTestResult.success}
        >
            <h3>{llmTestResult.success ? "✅ Success" : "❌ Failed"}</h3>
            <p>{llmTestResult.message || llmTestResult.error}</p>
            {#if llmTestResult.response}
                <p class="response">Response: {llmTestResult.response}</p>
            {/if}
        </div>
    {/if}
</div>

<style>
    .admin-card {
        background: linear-gradient(
            135deg,
            rgba(102, 126, 234, 0.05) 0%,
            rgba(118, 75, 162, 0.05) 100%
        );
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }

    .admin-card h2 {
        font-size: 1.5rem;
        margin: 0 0 0.75rem 0;
        color: #e0e0e0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .status-badge {
        font-size: 0.8rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 500;
    }

    .status-badge.configured {
        background: rgba(76, 175, 80, 0.2);
        color: #81c784;
    }

    .status-badge.not-configured {
        background: rgba(255, 152, 0, 0.2);
        color: #ffb74d;
    }

    .description {
        color: #a0a0a0;
        margin: 0 0 1.5rem 0;
        line-height: 1.5;
    }

    .config-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .form-group label {
        color: #a0a0a0;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .form-group input,
    .form-group select {
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 6px;
        color: #e0e0e0;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }

    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .action-buttons {
        display: flex;
        gap: 1rem;
    }

    .test-button,
    .save-button {
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .test-button {
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.4);
    }

    .test-button:hover:not(:disabled) {
        background: rgba(102, 126, 234, 0.3);
    }

    .save-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .save-button:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }

    .test-button:disabled,
    .save-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .result-box {
        margin-top: 1.5rem;
        padding: 1.5rem;
        border-radius: 8px;
        border-width: 1px;
        border-style: solid;
    }

    .result-box.success {
        background: rgba(76, 175, 80, 0.1);
        border-color: rgba(76, 175, 80, 0.3);
    }

    .result-box.error {
        background: rgba(244, 67, 54, 0.1);
        border-color: rgba(244, 67, 54, 0.3);
    }

    .result-box h3 {
        margin: 0 0 0.75rem 0;
        font-size: 1.125rem;
        color: #e0e0e0;
    }

    .result-box p {
        margin: 0.5rem 0;
        color: #c0c0c0;
    }

    .response {
        font-style: italic;
        color: #a0a0a0;
    }
</style>
