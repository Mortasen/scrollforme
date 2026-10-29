<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';
	import type { AgentConfig } from '#lib/api/client.js';

	let { agent = $bindable() }: { agent: AgentConfig } = $props();
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>How much may each visit cost?</Card.Title>
		<Card.Description>Caps for each site visit, so a run can never scroll forever.</Card.Description
		>
	</Card.Header>
	<Card.Content class="grid gap-4 sm:grid-cols-2">
		<div class="space-y-1">
			<Label for="model">Model</Label>
			<Input id="model" bind:value={agent.model} />
		</div>
		<div class="space-y-1">
			<Label for="effort">Effort (low, medium, high)</Label>
			<Input id="effort" bind:value={agent.effort} />
		</div>
		<div class="space-y-1">
			<Label for="max-turns">Most agent turns per site</Label>
			<Input id="max-turns" type="number" min="1" bind:value={agent.max_turns} />
		</div>
		<div class="space-y-1">
			<Label for="budget">Most dollars per site</Label>
			<Input id="budget" type="number" min="0.05" step="0.05" bind:value={agent.max_budget_usd} />
		</div>
	</Card.Content>
</Card.Root>
