<script lang="ts">
	import { untrack } from 'svelte';
	import { Button } from '#lib/components/ui/button/index.js';
	import { sendJson, type RawConfig } from '#lib/api/client.js';
	import SitesStep from './SitesStep.svelte';
	import BrowserStep from './BrowserStep.svelte';
	import ChecksStep from './ChecksStep.svelte';
	import LimitsStep from './LimitsStep.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	// An editable copy of the loaded config; saving writes it back.
	let config: RawConfig = $state(untrack(() => structuredClone(data.config) as RawConfig));
	let saved = $state(untrack(() => data.exists));
	let saving = $state(false);
	let error = $state('');
	const ready = $derived(
		config.sources.length > 0 && config.sources.every((source) => source.description.trim())
	);

	async function save() {
		saving = true;
		error = '';
		try {
			await sendJson('PUT', '/api/config', { config: $state.snapshot(config) });
			saved = true;
		} catch (problem) {
			error = (problem as Error).message;
		} finally {
			saving = false;
		}
	}
</script>

<main class="mx-auto max-w-2xl space-y-6 p-4 sm:p-8">
	<header class="space-y-1">
		<h1 class="text-2xl font-semibold">Set up scrollforme</h1>
		<p class="text-muted-foreground">
			Tell it which sites you check and why. It reads them for you and hands back one page that
			ends.
		</p>
	</header>
	<BrowserStep bind:kind={config.browser.kind} />
	<ChecksStep checks={data.checks} />
	<SitesStep modules={data.modules} bind:sources={config.sources} />
	<LimitsStep bind:agent={config.agent} />
	<div class="flex flex-wrap items-center gap-3">
		<Button disabled={!ready || saving} onclick={save}>{saving ? 'Saving…' : 'Save setup'}</Button>
		{#if saved}<Button variant="outline" href="/dashboard">Go to the dashboard</Button>{/if}
		{#if !ready}
			<p class="text-sm text-muted-foreground">Pick at least one site and describe each.</p>
		{/if}
		{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}
	</div>
</main>
