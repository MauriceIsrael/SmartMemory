<script lang="ts">
	import { runInference, type InferenceRunResponse } from "$lib/api";
	import {
		getInferenceEngines,
		updateInferenceEngine,
		type InferenceEngines,
		getLLMConfig,
		saveLLMConfig,
		testLLMConfig,
		type LLMConfig,
		type LLMConfigResponse,
		type LLMTestResult,
	} from "$lib/services/AdminService";
	import ToggleSwitch from "$lib/components/ToggleSwitch.svelte";
	import LLMConfigCard from "$lib/components/LLMConfigCard.svelte";
	import { onMount } from "svelte";

	let running = false;
	let result: InferenceRunResponse | null = null;
	let error: string | null = null;

	// Inference engines state
	let engines: InferenceEngines | null = null;
	let loadingEngines = false;
	let engineError: string | null = null;

	// LLM Configuration state
	let llmConfigured = false;
	let llmConfig: LLMConfig = {
		provider: "ollama",
		model: "llama3",
		base_url: "http://localhost:11434",
		temperature: 0.7,
	};
	let loadingLLM = false;
	let savingLLM = false;
	let testingLLM = false;
	let llmError: string | null = null;
	let llmTestResult: LLMTestResult | null = null;

	// Fetch engine states and LLM config on mount
	onMount(async () => {
		await fetchEngineStates();
		await fetchLLMConfig();
	});

	async function fetchEngineStates() {
		loadingEngines = true;
		engineError = null;
		try {
			engines = await getInferenceEngines();
		} catch (e) {
			engineError =
				e instanceof Error ? e.message : "Failed to load engine states";
		} finally {
			loadingEngines = false;
		}
	}

	async function handleEngineToggle(
		engineName: "owl_reasoning" | "sparql_rules",
		enabled: boolean,
	) {
		try {
			const updatedEngine = await updateInferenceEngine(
				engineName,
				enabled,
			);
			if (engines) {
				engines[engineName] = updatedEngine;
			}
		} catch (e) {
			engineError =
				e instanceof Error
					? e.message
					: `Failed to update ${engineName}`;
			// Revert the toggle on error
			await fetchEngineStates();
		}
	}

	async function handleRunInference() {
		running = true;
		error = null;
		result = null;

		try {
			result = await runInference();
		} catch (e) {
			error = e instanceof Error ? e.message : "Failed to run inference";
		} finally {
			running = false;
		}
	}

	async function fetchLLMConfig() {
		loadingLLM = true;
		llmError = null;
		try {
			const response = await getLLMConfig();
			llmConfigured = response.configured;
			if (response.config) {
				llmConfig = response.config;
			}
		} catch (e) {
			llmError =
				e instanceof Error ? e.message : "Failed to load LLM config";
		} finally {
			loadingLLM = false;
		}
	}

	async function handleSaveLLMConfig() {
		savingLLM = true;
		llmError = null;
		llmTestResult = null;
		try {
			await saveLLMConfig(llmConfig);
			llmConfigured = true;
			llmError = null;
		} catch (e) {
			llmError =
				e instanceof Error ? e.message : "Failed to save LLM config";
		} finally {
			savingLLM = false;
		}
	}

	async function handleTestLLMConfig() {
		testingLLM = true;
		llmTestResult = null;
		llmError = null;
		try {
			llmTestResult = await testLLMConfig();
		} catch (e) {
			llmError =
				e instanceof Error ? e.message : "Failed to test LLM config";
		} finally {
			testingLLM = false;
		}
	}
</script>

<div class="page">
	<header class="page-header">
		<h1>Administration Console</h1>
		<p class="page-description">
			Manage inference engines and trigger system operations
		</p>
	</header>

	<!-- Inference Engines Management -->
	<div class="admin-card">
		<h2>Inference Engines</h2>
		<p class="description">
			Activate or deactivate inference engines. When enabled, the
			corresponding rules will be loaded and used during inference runs.
		</p>

		{#if loadingEngines}
			<div class="loading-message">Loading engine states...</div>
		{:else if engineError}
			<div class="result-box error">
				<h3>❌ Error</h3>
				<p>{engineError}</p>
			</div>
		{:else if engines}
			<div class="engines-grid">
				<div class="engine-item">
					<div class="engine-info">
						<h3>{engines.owl_reasoning.name}</h3>
						<p
							class="engine-status"
							class:enabled={engines.owl_reasoning.enabled}
						>
							{engines.owl_reasoning.enabled
								? "✓ Active"
								: "○ Inactive"}
						</p>
					</div>
					<ToggleSwitch
						checked={engines.owl_reasoning.enabled}
						label=""
						onToggle={(value) =>
							handleEngineToggle("owl_reasoning", value)}
					/>
				</div>

				<div class="engine-item">
					<div class="engine-info">
						<h3>{engines.sparql_rules.name}</h3>
						<p
							class="engine-status"
							class:enabled={engines.sparql_rules.enabled}
						>
							{engines.sparql_rules.enabled
								? "✓ Active"
								: "○ Inactive"}
						</p>
					</div>
					<ToggleSwitch
						checked={engines.sparql_rules.enabled}
						label=""
						onToggle={(value) =>
							handleEngineToggle("sparql_rules", value)}
					/>
				</div>
			</div>
		{/if}
	</div>

	<!-- Manual Inference Trigger -->
	<div class="admin-card">
		<h2>Manual Inference Trigger</h2>
		<p class="description">
			Manually trigger a full inference run. This will execute all active
			inference rules on the knowledge graph.
		</p>

		<button
			on:click={handleRunInference}
			disabled={running}
			class="run-button"
		>
			{#if running}
				<span class="button-spinner"></span>
				Running Inference...
			{:else}
				▶️ Run Inference
			{/if}
		</button>

		{#if result}
			<div
				class="result-box"
				class:success={result.status === "success"}
				class:error={result.status === "error"}
			>
				<h3>
					{result.status === "success" ? "✅ Success" : "❌ Error"}
				</h3>
				<p>{result.message}</p>
				{#if result.triples_inferred > 0}
					<p class="stat-highlight">
						{result.triples_inferred} triples inferred
					</p>
				{/if}
			</div>
		{/if}

		{#if error}
			<div class="result-box error">
				<h3>❌ Error</h3>
				<p>{error}</p>
			</div>
		{/if}
	</div>

	<!-- LLM Configuration -->
	<LLMConfigCard
		bind:llmConfig
		bind:llmConfigured
		bind:savingLLM
		bind:testingLLM
		bind:llmError
		bind:llmTestResult
		onSave={handleSaveLLMConfig}
		onTest={handleTestLLMConfig}
	/>

	<div class="admin-card">
		<h2>System Information</h2>
		<div class="info-grid">
			<div class="info-item">
				<span class="info-label">Backend API:</span>
				<span class="info-value">{window.location.origin}</span>
			</div>
			<div class="info-item">
				<span class="info-label">API Documentation:</span>
				<span class="info-value">
					<a
						href="{window.location.origin}/docs"
						target="_blank"
						class="link">{window.location.origin}/docs</a
					>
				</span>
			</div>
		</div>
	</div>
</div>

<style>
	.page {
		padding: 2rem;
		max-width: 1000px;
	}

	.page-header {
		margin-bottom: 2rem;
	}

	.page-header h1 {
		font-size: 2.5rem;
		font-weight: 700;
		margin: 0 0 0.5rem 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.page-description {
		color: #a0a0a0;
		margin: 0;
	}

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
	}

	.description {
		color: #a0a0a0;
		margin: 0 0 1.5rem 0;
		line-height: 1.5;
	}

	.run-button {
		padding: 1rem 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border: none;
		border-radius: 8px;
		color: white;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.run-button:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
	}

	.run-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.button-spinner {
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
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

	.stat-highlight {
		font-weight: 600;
		color: #81c784 !important;
		margin-top: 1rem !important;
	}

	.info-grid {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.info-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 8px;
	}

	.info-label {
		color: #a0a0a0;
		font-size: 0.9rem;
	}

	.info-value {
		color: #e0e0e0;
		font-weight: 500;
		font-size: 0.9rem;
	}

	.link {
		color: #667eea;
		text-decoration: none;
		transition: color 0.2s ease;
	}

	.link:hover {
		color: #764ba2;
		text-decoration: underline;
	}

	.engines-grid {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.engine-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem 1.5rem;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(102, 126, 234, 0.2);
		border-radius: 8px;
		transition: all 0.2s ease;
	}

	.engine-item:hover {
		background: rgba(255, 255, 255, 0.05);
		border-color: rgba(102, 126, 234, 0.3);
	}

	.engine-info h3 {
		margin: 0 0 0.25rem 0;
		font-size: 1.125rem;
		color: #e0e0e0;
	}

	.engine-status {
		margin: 0;
		font-size: 0.875rem;
		color: #a0a0a0;
	}

	.engine-status.enabled {
		color: #81c784;
		font-weight: 500;
	}

	.loading-message {
		color: #a0a0a0;
		text-align: center;
		padding: 2rem;
	}
</style>
