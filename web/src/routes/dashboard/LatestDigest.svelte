<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Badge } from '#lib/components/ui/badge/index.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import { digestUrl, type RunSummary } from '#lib/api/client.js';

	let { run }: { run: RunSummary } = $props();
	const ok = $derived(run.sites.filter((site) => !run.failed.includes(site)));
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Your latest digest</Card.Title>
		<Card.Description>Collected {new Date(run.generated_at).toLocaleString()}</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-3">
		<div class="flex flex-wrap gap-1">
			{#each ok as site (site)}<Badge variant="secondary">{site}</Badge>{/each}
			{#each run.failed as site (site)}<Badge variant="destructive">{site} failed</Badge>{/each}
		</div>
		<Button href={digestUrl(run.id)} target="_blank">Read it</Button>
	</Card.Content>
</Card.Root>
