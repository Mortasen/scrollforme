<script lang="ts">
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import * as Card from '#lib/components/ui/card/index.js';
	import type { Check } from '#lib/api/client.js';

	let { checks }: { checks: Check[] } = $props();
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>1. Check this machine</Card.Title>
		<Card.Description>
			scrollforme runs locally: Chrome, the stealth browser server and a browser profile of its own.
		</Card.Description>
	</Card.Header>
	<Card.Content>
		<ul class="space-y-2">
			{#each checks as check (check.name)}
				<li class="flex items-start gap-2">
					{#if check.ok}
						<CircleCheck class="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
					{:else}
						<CircleAlert class="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden="true" />
					{/if}
					<div class="min-w-0">
						<p class="text-sm font-medium">
							{check.name}: {check.ok ? 'found' : 'missing'}
						</p>
						<p class="text-xs break-all text-muted-foreground">{check.detail}</p>
					</div>
				</li>
			{/each}
		</ul>
		<p class="mt-3 text-xs text-muted-foreground">
			A missing browser profile is expected before your first login (step 4).
		</p>
	</Card.Content>
</Card.Root>
