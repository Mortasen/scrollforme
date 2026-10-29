<script lang="ts">
	import { Button } from '#lib/components/ui/button/index.js';

	let {
		canGoBack,
		canGoOn,
		last,
		saving,
		onback,
		onnext
	}: {
		canGoBack: boolean;
		canGoOn: boolean;
		last: boolean;
		saving: boolean;
		onback: () => void;
		onnext: () => void;
	} = $props();
</script>

<div class="flex items-center justify-between gap-3">
	<Button variant="ghost" disabled={!canGoBack} onclick={onback}>Back</Button>
	<Button disabled={!canGoOn} onclick={onnext}>
		{#if last}{saving ? 'Saving…' : 'Finish'}{:else}Next{/if}
	</Button>
</div>
