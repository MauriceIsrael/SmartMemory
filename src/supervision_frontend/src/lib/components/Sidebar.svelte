<script lang="ts">
	import { page } from '$app/stores';

	const navItems = [
		{ path: '/', label: 'Dashboard', icon: '📊' },
		{ path: '/facts', label: 'Fact Explorer', icon: '🔍' },
		{ path: '/rules', label: 'Rule Management', icon: '⚙️' },
		{ path: '/admin', label: 'Administration', icon: '🛠️' }
	];
</script>

<nav class="sidebar">
	<div class="sidebar-header">
		<h1>🧠 SmartMemory</h1>
		<p class="subtitle">Supervision Dashboard</p>
	</div>

	<ul class="nav-list">
		{#each navItems as item}
			<li>
				<a href={item.path} class:active={$page.url.pathname === item.path}>
					<span class="icon">{item.icon}</span>
					<span class="label">{item.label}</span>
				</a>
			</li>
		{/each}
	</ul>
</nav>

<style>
	.sidebar {
		width: 260px;
		height: 100vh;
		background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
		color: #e0e0e0;
		display: flex;
		flex-direction: column;
		padding: 2rem 0;
		box-shadow: 4px 0 10px rgba(0, 0, 0, 0.3);
	}

	.sidebar-header {
		padding: 0 1.5rem 1.5rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.sidebar-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		margin: 0 0 0.5rem 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		font-size: 0.75rem;
		color: #a0a0a0;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 1px;
	}

	.nav-list {
		list-style: none;
		padding: 1.5rem 0;
		margin: 0;
		flex: 1;
	}

	.nav-list li {
		margin: 0.25rem 0;
	}

	.nav-list a {
		display: flex;
		align-items: center;
		padding: 0.875rem 1.5rem;
		color: #e0e0e0;
		text-decoration: none;
		transition: all 0.2s ease;
		position: relative;
	}

	.nav-list a::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		width: 3px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		transform: scaleY(0);
		transition: transform 0.2s ease;
	}

	.nav-list a:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	.nav-list a.active {
		background: rgba(102, 126, 234, 0.15);
		color: #fff;
	}

	.nav-list a.active::before {
		transform: scaleY(1);
	}

	.icon {
		font-size: 1.25rem;
		margin-right: 0.75rem;
	}

	.label {
		font-size: 0.9rem;
		font-weight: 500;
	}
</style>
