<script lang="ts">
	import { onMount, onDestroy } from "svelte";
	import { fetchRules, toggleRule, type InferenceRule } from "$lib/api";
	import { getRules } from "$lib/services/AdminService";

	let rules: InferenceRule[] = [];
	let loading = true;
	let isInitialLoad = true;
	let error: string | null = null;
	let toastMessage = "";
	let showToast = false;
	let sourceFilter: "all" | "default" | "dynamic" = "all";
	let refreshInterval: number;

	async function loadRules() {
		// Only show loading spinner on initial load, not on refresh
		if (isInitialLoad) {
			loading = true;
		}

		error = null;
		try {
			// Use AdminService getRules with filtering
			const filterParam =
				sourceFilter === "all" ? undefined : sourceFilter;
			rules = await getRules(filterParam);
			error = null;
		} catch (e) {
			error = e instanceof Error ? e.message : "Failed to load rules";
		} finally {
			loading = false;
			isInitialLoad = false;
		}
	}

	onMount(async () => {
		await loadRules();

		// Auto-refresh every 5 seconds
		refreshInterval = window.setInterval(loadRules, 5000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function handleToggle(ruleId: string) {
		try {
			const updatedRule = await toggleRule(ruleId);
			// Update the rule in our local state
			rules = rules.map((r) => (r.id === ruleId ? updatedRule : r));
			showMessage(
				`Rule "${ruleId}" ${updatedRule.is_active ? "activated" : "deactivated"}`,
			);
		} catch (e) {
			showMessage(
				`Failed to toggle rule: ${e instanceof Error ? e.message : "Unknown error"}`,
				true,
			);
		}
	}

	function showMessage(message: string, isError = false) {
		toastMessage = message;
		showToast = true;
		setTimeout(() => {
			showToast = false;
		}, 3000);
	}

	// Reload rules when filter changes
	$: if (sourceFilter) {
		loadRules();
	}
</script>

<div class="page">
	<header class="page-header">
		<div class="header-content">
			<div>
				<h1>Rule Management</h1>
				<p class="page-description">
					Manage and monitor inference rules
				</p>
			</div>
			<div class="filter-controls">
				<label for="source-filter">Filter by source:</label>
				<select
					id="source-filter"
					bind:value={sourceFilter}
					class="filter-select"
				>
					<option value="all">All Rules</option>
					<option value="default">Default Rules</option>
					<option value="dynamic">Dynamically Loaded</option>
				</select>
			</div>
		</div>
	</header>

	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Loading rules...</p>
		</div>
	{:else if error}
		<div class="error-state">
			<p class="error-icon">⚠️</p>
			<p>{error}</p>
		</div>
	{:else if rules.length === 0}
		<div class="empty-state">
			<p class="empty-icon">📋</p>
			<h2>No inference rules found</h2>
			<p>No inference rules are configured in the system.</p>
		</div>
	{:else}
		<div class="rules-container">
			{#each rules as rule}
				<div class="rule-card" class:inactive={!rule.is_active}>
					<div class="rule-header">
						<div class="rule-info">
							<h3 class="rule-name">{rule.id}</h3>
							<p class="rule-description">{rule.description}</p>
							{#if rule.validation_error}
								<p
									class="rule-error"
									title={rule.validation_error}
								>
									⚠️ Validation Error: {rule.validation_error}
								</p>
							{/if}
						</div>
						<label class="toggle-switch">
							<input
								type="checkbox"
								checked={rule.is_active}
								on:change={() => handleToggle(rule.id)}
							/>
							<span class="slider"></span>
						</label>
					</div>

					<div class="rule-stats">
						<div class="stat">
							<span class="stat-label">Executions:</span>
							<span class="stat-value"
								>{rule.execution_count}</span
							>
						</div>
						<div class="stat">
							<span class="stat-label">Triples Generated:</span>
							<span class="stat-value"
								>{rule.triples_generated}</span
							>
						</div>
					</div>

					<details class="rule-query">
						<summary>View SPARQL Query</summary>
						<pre class="query-code">{rule.sparql_query}</pre>
					</details>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showToast}
	<div class="toast">{toastMessage}</div>
{/if}

<style>
	.page {
		padding: 2rem;
		max-width: 1200px;
	}

	.page-header {
		margin-bottom: 2rem;
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 2rem;
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

	.filter-controls {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.filter-controls label {
		color: #a0a0a0;
		font-size: 0.9rem;
		white-space: nowrap;
	}

	.filter-select {
		padding: 0.5rem 1rem;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(102, 126, 234, 0.3);
		border-radius: 6px;
		color: #e0e0e0;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.filter-select:hover {
		background: rgba(255, 255, 255, 0.08);
		border-color: rgba(102, 126, 234, 0.5);
	}

	.filter-select:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
	}

	.rules-container {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.rule-card {
		background: linear-gradient(
			135deg,
			rgba(102, 126, 234, 0.05) 0%,
			rgba(118, 75, 162, 0.05) 100%
		);
		border: 1px solid rgba(102, 126, 234, 0.2);
		border-radius: 12px;
		padding: 1.5rem;
		transition: all 0.3s ease;
	}

	.rule-card.inactive {
		opacity: 0.6;
		background: rgba(255, 255, 255, 0.02);
		border-color: rgba(255, 255, 255, 0.1);
	}

	.rule-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
	}

	.rule-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1rem;
	}

	.rule-info {
		flex: 1;
	}

	.rule-name {
		font-size: 1.25rem;
		color: #e0e0e0;
		margin: 0 0 0.5rem 0;
	}

	.rule-description {
		color: #a0a0a0;
		margin: 0;
		font-size: 0.9rem;
	}

	.rule-error {
		color: #ff6b6b;
		margin: 0.5rem 0 0 0;
		font-size: 0.85rem;
	}

	.toggle-switch {
		position: relative;
		display: inline-block;
		width: 56px;
		height: 30px;
	}

	.toggle-switch input {
		opacity: 0;
		width: 0;
		height: 0;
	}

	.slider {
		position: absolute;
		cursor: pointer;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(255, 255, 255, 0.1);
		transition: 0.3s;
		border-radius: 30px;
	}

	.slider:before {
		position: absolute;
		content: "";
		height: 22px;
		width: 22px;
		left: 4px;
		bottom: 4px;
		background-color: #808080;
		transition: 0.3s;
		border-radius: 50%;
	}

	input:checked + .slider {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}

	input:checked + .slider:before {
		transform: translateX(26px);
		background-color: white;
	}

	.rule-stats {
		display: flex;
		gap: 2rem;
		margin-bottom: 1rem;
		padding-top: 1rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.stat {
		display: flex;
		gap: 0.5rem;
	}

	.stat-label {
		color: #a0a0a0;
		font-size: 0.875rem;
	}

	.stat-value {
		color: #e0e0e0;
		font-weight: 600;
		font-size: 0.875rem;
	}

	.rule-query {
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.rule-query summary {
		cursor: pointer;
		color: #667eea;
		font-size: 0.9rem;
		user-select: none;
	}

	.rule-query summary:hover {
		color: #764ba2;
	}

	.query-code {
		margin: 1rem 0 0 0;
		padding: 1rem;
		background: rgba(0, 0, 0, 0.3);
		border: 1px solid rgba(102, 126, 234, 0.2);
		border-radius: 8px;
		overflow-x: auto;
		font-size: 0.85rem;
		color: #c0c0c0;
		line-height: 1.5;
	}

	.toast {
		position: fixed;
		bottom: 2rem;
		right: 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 1rem 1.5rem;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
		animation: slideIn 0.3s ease;
		z-index: 1000;
	}

	@keyframes slideIn {
		from {
			transform: translateY(100%);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.loading-state,
	.error-state,
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		text-align: center;
	}

	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid rgba(102, 126, 234, 0.2);
		border-top-color: #667eea;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error-icon,
	.empty-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
	}

	.empty-state h2 {
		color: #e0e0e0;
		margin: 0 0 0.5rem 0;
	}

	.empty-state p {
		color: #a0a0a0;
	}
</style>
