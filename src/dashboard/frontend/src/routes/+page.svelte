<script lang="ts">
	import { onMount, onDestroy } from "svelte";
	import { fetchStats, type SystemStats } from "$lib/api";
	import StatCard from "$lib/components/StatCard.svelte";

	let stats: SystemStats | null = null;
	let loading = true;
	let isInitialLoad = true;
	let error: string | null = null;
	let refreshInterval: number;

	async function loadStats() {
		// Only show loading spinner on initial load, not on refresh
		if (isInitialLoad) {
			loading = true;
		}

		try {
			stats = await fetchStats();
			error = null;
		} catch (e) {
			error = e instanceof Error ? e.message : "Failed to load stats";
		} finally {
			loading = false;
			isInitialLoad = false;
		}
	}

	onMount(async () => {
		await loadStats();

		// Auto-refresh every 5 seconds
		refreshInterval = window.setInterval(loadStats, 5000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	$: inferredPercentage =
		stats && stats.total_triplets > 0
			? (
					(stats.inferred_triplet_count / stats.total_triplets) *
					100
				).toFixed(1)
			: "0";
</script>

<div class="dashboard">
	<header class="page-header">
		<h1>Dashboard</h1>
		<p class="page-description">
			Real-time insights into your SmartMemory knowledge graph
		</p>
	</header>

	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Loading statistics...</p>
		</div>
	{:else if error}
		<div class="error-state">
			<p class="error-icon">⚠️</p>
			<h2>Connection Error</h2>
			<p>{error}</p>
			<p class="error-hint">Make sure the backend API is running</p>
		</div>
	{:else if stats}
		<div class="stats-grid">
			<a href="/facts" class="stat-link">
				<StatCard
					title="Total Facts"
					value={stats.total_triplets.toLocaleString()}
					icon="📚"
					subtitle="Triples in knowledge graph"
				/>
			</a>
			<a href="/facts?origin=inferred" class="stat-link">
				<StatCard
					title="Inferred Facts"
					value={`${inferredPercentage}%`}
					icon="🤖"
					subtitle={`${stats.inferred_triplet_count.toLocaleString()} of ${stats.total_triplets.toLocaleString()}`}
				/>
			</a>
			<a href="/rules" class="stat-link">
				<StatCard
					title="Active Rules"
					value={stats.active_rule_count}
					icon="✅"
					subtitle={`${stats.inactive_rule_count} inactive`}
				/>
			</a>
		</div>

		<div class="info-card">
			<h2>System Overview</h2>
			<div class="info-grid">
				<div class="info-item">
					<span class="info-label">Asserted Facts:</span>
					<span class="info-value"
						>{stats.asserted_triplet_count.toLocaleString()}</span
					>
				</div>
				<div class="info-item">
					<span class="info-label">Inferred Facts:</span>
					<span class="info-value"
						>{stats.inferred_triplet_count.toLocaleString()}</span
					>
				</div>
				<div class="info-item">
					<span class="info-label">Total Rules:</span>
					<span class="info-value"
						>{stats.active_rule_count +
							stats.inactive_rule_count}</span
					>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.dashboard {
		padding: 2rem;
		max-width: 1200px;
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
		font-size: 1rem;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.stat-link {
		text-decoration: none;
		color: inherit;
		display: block;
		transition: transform 0.2s ease;
	}

	.stat-link:hover {
		transform: translateY(-4px);
	}

	.info-card {
		background: linear-gradient(
			135deg,
			rgba(102, 126, 234, 0.05) 0%,
			rgba(118, 75, 162, 0.05) 100%
		);
		border: 1px solid rgba(102, 126, 234, 0.15);
		border-radius: 12px;
		padding: 1.5rem;
		backdrop-filter: blur(10px);
	}

	.info-card h2 {
		font-size: 1.25rem;
		margin: 0 0 1rem 0;
		color: #e0e0e0;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
		font-weight: 600;
		font-size: 1rem;
	}

	.loading-state,
	.error-state {
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

	.error-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
	}

	.error-state h2 {
		color: #ff6b6b;
		margin: 0 0 0.5rem 0;
	}

	.error-state p {
		color: #a0a0a0;
		margin: 0.5rem 0;
	}

	.error-hint {
		font-size: 0.875rem;
		color: #808080;
		font-style: italic;
	}
</style>
