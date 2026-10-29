<script lang="ts">
	import { untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { sendJson, type RawConfig } from '#lib/api/client.js';
	import WizardStep from './WizardStep.svelte';
	import WizardNav from './WizardNav.svelte';
	import { isAnswered, stepsFor } from './steps.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	// An editable copy of the loaded config; finishing writes it back.
	let config: RawConfig = $state(untrack(() => structuredClone(data.config) as RawConfig));
	let index = $state(0);
	let saving = $state(false);
	let error = $state('');

	const steps = $derived(stepsFor(config));
	const step = $derived(steps[Math.min(index, steps.length - 1)]);
	const last = $derived(index >= steps.length - 1);

	async function finish() {
		saving = true;
		error = '';
		try {
			await sendJson('PUT', '/api/config', { config: $state.snapshot(config) });
			await goto(resolve('/dashboard'));
		} catch (problem) {
			error = (problem as Error).message;
		} finally {
			saving = false;
		}
	}
</script>

<main class="mx-auto flex min-h-svh max-w-xl flex-col justify-center gap-6 p-4 sm:p-8">
	<p class="text-sm text-muted-foreground">Step {index + 1} of {steps.length}</p>
	{#key index}
		<WizardStep {step} checks={data.checks} modules={data.modules} bind:config />
	{/key}
	<WizardNav
		canGoBack={index > 0}
		canGoOn={isAnswered(step, config) && !saving}
		{last}
		{saving}
		onback={() => (index -= 1)}
		onnext={() => (last ? finish() : (index += 1))}
	/>
	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}
</main>
