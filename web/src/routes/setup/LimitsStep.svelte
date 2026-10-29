<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';
	import type { AgentConfig } from '#lib/api/client.js';

	let { agent = $bindable() }: { agent: AgentConfig } = $props();
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>How much may each site visit cost at most?</Card.Title>
		<Card.Description>
			A hard cap in US dollars, so a visit can never scroll forever.
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-1">
		<Label for="budget">Dollars per site visit</Label>
		<Input id="budget" type="number" min="0.05" step="0.05" bind:value={agent.max_budget_usd} />
	</Card.Content>
</Card.Root>
