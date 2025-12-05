<script lang="ts">
	export let title: string;
	export let value: string | number;
	export let subtitle: string = '';
	export let icon: string = '📊';
</script>

<div class="stat-card">
	<div class="card-icon">{icon}</div>
	<div class="card-content">
		<h3 class="card-title">{title}</h3>
		<p class="card-value">{value}</p>
		{#if subtitle}
			<p class="card-subtitle">{subtitle}</p>
		{/if}
	</div>
</div>

<style>
	.stat-card {
		background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
		border: 1px solid rgba(102, 126, 234, 0.2);
		border-radius: 12px;
		padding: 1.5rem;
		display: flex;
		align-items: center;
		gap: 1rem;
		transition: all 0.3s ease;
		backdrop-filter: blur(10px);
	}

	.stat-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
		border-color: rgba(102, 126, 234, 0.4);
	}

	.card-icon {
		font-size: 2.5rem;
		filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
	}

	.card-content {
		flex: 1;
	}

	.card-title {
		font-size: 0.875rem;
		color: #a0a0a0;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin: 0 0 0.5rem 0;
		font-weight: 600;
	}

	.card-value {
		font-size: 2rem;
		font-weight: 700;
		margin: 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.card-subtitle {
		font-size: 0.75rem;
		color: #808080;
		margin: 0.25rem 0 0 0;
	}
</style>
