<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import '../app.css';
</script>

<div class="app-container">
	<Sidebar />
	<main class="main-content">
		<slot />
	</main>
</div>

<style>
	.app-container {
		display: flex;
		min-height: 100vh;
		background: #0f0f1e;
		color: #e0e0e0;
	}

	.main-content {
		flex: 1;
		overflow-y: auto;
	}
</style>
