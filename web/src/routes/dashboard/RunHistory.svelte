<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Badge } from '#lib/components/ui/badge/index.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import { digestUrl, type RunSummary } from '#lib/api/client.js';

	let { runs }: { runs: RunSummary[] } = $props();
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Earlier digests</Card.Title>
	</Card.Header>
	<Card.Content>
		{#if runs.length === 0}
			<p class="text-sm text-muted-foreground">No earlier digests.</p>
		{:else}
			<ul class="divide-y">
				{#each runs as run (run.id)}
					<li class="flex flex-wrap items-center justify-between gap-2 py-2">
						<Button variant="link" class="h-auto p-0" href={digestUrl(run.id)} target="_blank">
							{new Date(run.generated_at).toLocaleString()}
						</Button>
						<span class="flex flex-wrap gap-1">
							{#each run.failed as module (module)}
								<Badge variant="destructive">{module} failed</Badge>
							{/each}
						</span>
					</li>
				{/each}
			</ul>
		{/if}
	</Card.Content>
</Card.Root>
