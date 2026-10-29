<script lang="ts">
	import { Button } from '#lib/components/ui/button/index.js';
	import RunPanel from './RunPanel.svelte';
	import RunHistory from './RunHistory.svelte';
	import LatestDigest from './LatestDigest.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const latest = $derived(data.runs[0]);
</script>

<main class="mx-auto max-w-2xl space-y-6 p-4 sm:p-8">
	<header class="flex flex-wrap items-end justify-between gap-2">
		<div>
			<h1 class="text-2xl font-semibold">scrollforme</h1>
			<p class="text-sm text-muted-foreground">
				{data.sources.map((source) => source.module).join(', ')} · read for you, then done.
			</p>
		</div>
		<Button variant="ghost" size="sm" href="/setup">Edit setup</Button>
	</header>
	{#if latest}
		<LatestDigest run={latest} />
	{:else}
		<p class="text-muted-foreground">No digest yet. Run it once to get your first page.</p>
	{/if}
	<RunPanel current={data.current} primary={!latest} />
	{#if data.runs.length > 1}<RunHistory runs={data.runs.slice(1)} />{/if}
</main>
