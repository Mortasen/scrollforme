<script lang="ts">
	import { onDestroy, untrack } from 'svelte';
	import { invalidateAll } from '$app/navigation';
	import * as Card from '#lib/components/ui/card/index.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import { getJson, sendJson, type RunState } from '#lib/api/client.js';

	let { current, primary }: { current: RunState; primary: boolean } = $props();
	// Starts from the loaded state, then follows the API on its own.
	let run: RunState = $state(untrack(() => current));
	let error = $state('');
	let timer: ReturnType<typeof setInterval> | undefined;

	const running = $derived(run.status === 'running');
	const progress = $derived(
		running ? `Reading ${run.current_module || '…'} (${run.index + 1} of ${run.total})` : ''
	);

	async function start() {
		error = '';
		try {
			run = await sendJson<RunState>('POST', '/api/runs');
			follow();
		} catch (problem) {
			error = (problem as Error).message;
		}
	}

	function follow() {
		clearInterval(timer);
		timer = setInterval(poll, 2000);
	}

	async function poll() {
		run = await getJson<RunState>('/api/runs/current');
		if (run.status !== 'running') {
			clearInterval(timer);
			await invalidateAll();
		}
	}

	if (untrack(() => current.status) === 'running') follow();
	onDestroy(() => clearInterval(timer));
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>{running ? 'Reading your sites' : 'Run'}</Card.Title>
		<Card.Description>
			{running ? progress : 'Visits each site once and writes a new digest.'}
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-2">
		<Button variant={primary ? 'default' : 'outline'} disabled={running} onclick={start}>
			{running ? 'Running…' : 'Run now'}
		</Button>
		{#if run.status === 'failed'}
			<p class="text-sm text-destructive" role="alert">The last run failed: {run.error}</p>
		{/if}
		{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}
	</Card.Content>
</Card.Root>
