<script lang="ts">
	import { onMount } from "svelte";
	import { fetchFacts, type Fact } from "$lib/api";
	import { getFacts } from "$lib/services/AdminService";

	let facts: Fact[] = [];
	let totalItems = 0;
	let currentPage = 1;
	let pageSize = 50;
	let search = "";
	let loading = true;
	let error: string | null = null;
	let originFilter: "all" | "explicit" | "inferred" = "all";

	async function loadFacts() {
		loading = true;
		error = null;
		try {
			// Use AdminService getFacts with filtering
			const originParam =
				originFilter === "all" ? undefined : originFilter;
			// Note: AdminService getFacts doesn't support pagination yet, using fetchFacts
			const response = await fetchFacts(
				currentPage,
				pageSize,
				search || undefined,
				originParam,
			);
			facts = response.items;
			totalItems = response.total_items;
		} catch (e) {
			error = e instanceof Error ? e.message : "Failed to load facts";
		} finally {
			loading = false;
		}
	}

	onMount(loadFacts);

	function handleSearch() {
		currentPage = 1;
		loadFacts();
	}

	function nextPage() {
		if (currentPage * pageSize < totalItems) {
			currentPage++;
			loadFacts();
		}
	}

	function prevPage() {
		if (currentPage > 1) {
			currentPage--;
			loadFacts();
		}
	}

	$: totalPages = Math.ceil(totalItems / pageSize);

	// Reload facts when filter changes
	$: if (originFilter) {
		currentPage = 1;
		loadFacts();
	}
</script>

<div class="page">
	<header class="page-header">
		<div class="header-content">
			<div>
				<h1>Fact Explorer</h1>
				<p class="page-description">
					Browse and search facts in the knowledge graph
				</p>
			</div>
			<div class="filter-controls">
				<label for="origin-filter">Filter by origin:</label>
				<select
					id="origin-filter"
					bind:value={originFilter}
					class="filter-select"
				>
					<option value="all">All Facts</option>
					<option value="explicit">Explicit Facts</option>
					<option value="inferred">Inferred Facts</option>
				</select>
			</div>
		</div>
	</header>

	<div class="search-bar">
		<input
			type="text"
			bind:value={search}
			on:keypress={(e) => e.key === "Enter" && handleSearch()}
			placeholder="Search facts by subject, predicate, or object..."
			class="search-input"
		/>
		<button on:click={handleSearch} class="search-button">Search</button>
	</div>

	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Loading facts...</p>
		</div>
	{:else if error}
		<div class="error-state">
			<p class="error-icon">⚠️</p>
			<p>{error}</p>
		</div>
	{:else if facts.length === 0}
		<div class="empty-state">
			<p class="empty-icon">📭</p>
			<h2>No facts found</h2>
			<p>
				The knowledge graph is empty or your search didn't match any
				facts.
			</p>
		</div>
	{:else}
		<div class="fact-table-container">
			<table class="fact-table">
				<thead>
					<tr>
						<th>Subject</th>
						<th>Predicate</th>
						<th>Object</th>
						<th>Type</th>
					</tr>
				</thead>
				<tbody>
					{#each facts as fact}
						<tr>
							<td class="cell-content">{fact.Subject}</td>
							<td class="cell-content">{fact.Predicate}</td>
							<td class="cell-content">{fact.Object}</td>
							<td>
								<span
									class="badge"
									class:badge-inferred={fact.Provenance ===
										"sparql-rule" ||
										fact.Provenance === "owlrl"}
									class:badge-asserted={fact.Provenance ===
										"user" ||
										fact.Provenance === "user-verified"}
								>
									{fact.Provenance === "sparql-rule" ||
									fact.Provenance === "owlrl"
										? "Inferred"
										: "Asserted"}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="pagination">
			<button
				on:click={prevPage}
				disabled={currentPage === 1}
				class="pagination-button">Previous</button
			>
			<span class="pagination-info">
				Page {currentPage} of {totalPages} ({totalItems} total facts)
			</span>
			<button
				on:click={nextPage}
				disabled={currentPage >= totalPages}
				class="pagination-button">Next</button
			>
		</div>
	{/if}
</div>

<style>
	.page {
		padding: 2rem;
		max-width: 1400px;
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

	.search-bar {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.search-input {
		flex: 1;
		padding: 0.875rem 1rem;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(102, 126, 234, 0.3);
		border-radius: 8px;
		color: #e0e0e0;
		font-size: 1rem;
		transition: all 0.2s ease;
	}

	.search-input:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.search-button {
		padding: 0.875rem 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border: none;
		border-radius: 8px;
		color: white;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.search-button:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}

	.fact-table-container {
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid rgba(102, 126, 234, 0.2);
		border-radius: 12px;
		overflow: hidden;
		margin-bottom: 1.5rem;
	}

	.fact-table {
		width: 100%;
		border-collapse: collapse;
	}

	.fact-table thead {
		background: rgba(102, 126, 234, 0.1);
	}

	.fact-table th {
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #e0e0e0;
		border-bottom: 1px solid rgba(102, 126, 234, 0.2);
	}

	.fact-table tbody tr {
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		transition: background 0.15s ease;
	}

	.fact-table tbody tr:hover {
		background: rgba(102, 126, 234, 0.05);
	}

	.fact-table td {
		padding: 1rem;
		color: #c0c0c0;
	}

	.cell-content {
		max-width: 300px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.badge-asserted {
		background: rgba(76, 175, 80, 0.2);
		color: #81c784;
		border: 1px solid rgba(76, 175, 80, 0.3);
	}

	.badge-inferred {
		background: rgba(102, 126, 234, 0.2);
		color: #9fa8da;
		border: 1px solid rgba(102, 126, 234, 0.3);
	}

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 2rem;
	}

	.pagination-button {
		padding: 0.75rem 1.5rem;
		background: rgba(102, 126, 234, 0.1);
		border: 1px solid rgba(102, 126, 234, 0.3);
		border-radius: 8px;
		color: #e0e0e0;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.pagination-button:hover:not(:disabled) {
		background: rgba(102, 126, 234, 0.2);
		border-color: #667eea;
	}

	.pagination-button:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.pagination-info {
		color: #a0a0a0;
		font-size: 0.9rem;
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
