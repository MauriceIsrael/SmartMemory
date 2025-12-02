<script lang="ts">
	/**
	 * Reusable Toggle Switch Component
	 * A styled toggle switch for boolean state management
	 */

	export let checked: boolean = false;
	export let disabled: boolean = false;
	export let label: string = '';
	export let onToggle: (value: boolean) => void = () => {};

	function handleToggle() {
		if (!disabled) {
			checked = !checked;
			onToggle(checked);
		}
	}
</script>

<div class="toggle-container">
	{#if label}
		<label class="toggle-label">{label}</label>
	{/if}
	<button
		class="toggle-switch"
		class:checked
		class:disabled
		on:click={handleToggle}
		aria-checked={checked}
		aria-label={label || 'Toggle switch'}
		role="switch"
		{disabled}
	>
		<span class="toggle-slider" />
	</button>
</div>

<style>
	.toggle-container {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.toggle-label {
		font-size: 14px;
		font-weight: 500;
		color: #333;
	}

	.toggle-switch {
		position: relative;
		width: 50px;
		height: 26px;
		background-color: #ccc;
		border-radius: 13px;
		border: none;
		cursor: pointer;
		transition: background-color 0.3s ease;
		outline: none;
	}

	.toggle-switch:focus-visible {
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
	}

	.toggle-switch.checked {
		background-color: #3b82f6;
	}

	.toggle-switch.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.toggle-slider {
		position: absolute;
		top: 2px;
		left: 2px;
		width: 22px;
		height: 22px;
		background-color: white;
		border-radius: 50%;
		transition: transform 0.3s ease;
	}

	.toggle-switch.checked .toggle-slider {
		transform: translateX(24px);
	}
</style>
