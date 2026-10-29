<script lang="ts">
	import type { Check, RawConfig } from '#lib/api/client.js';
	import SitesStep from './SitesStep.svelte';
	import ChecksStep from './ChecksStep.svelte';
	import LimitsStep from './LimitsStep.svelte';
	import BrowserStep from './BrowserStep.svelte';
	import DescribeStep from './DescribeStep.svelte';
	import type { Step } from './steps.js';

	let {
		step,
		checks,
		modules,
		config = $bindable()
	}: { step: Step; checks: Check[]; modules: string[]; config: RawConfig } = $props();

	const sourceIndex = $derived(
		step.kind === 'describe' ? config.sources.findIndex((s) => s.module === step.module) : -1
	);
</script>

{#if step.kind === 'browser'}
	<BrowserStep bind:kind={config.browser.kind} />
{:else if step.kind === 'checks'}
	<ChecksStep {checks} />
{:else if step.kind === 'sites'}
	<SitesStep {modules} bind:sources={config.sources} />
{:else if step.kind === 'describe' && sourceIndex >= 0}
	<DescribeStep bind:source={config.sources[sourceIndex]} />
{:else if step.kind === 'limits'}
	<LimitsStep bind:agent={config.agent} />
{/if}
