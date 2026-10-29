<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Label } from '#lib/components/ui/label/index.js';

	let { kind = $bindable() }: { kind: string } = $props();
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Which browser do you use every day?</Card.Title>
		<Card.Description>
			scrollforme reads your sites in that browser, with the logins you already have.
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-3">
		<div class="flex gap-6">
			<div class="flex items-center gap-2">
				<input id="kind-chrome" type="radio" value="chrome" bind:group={kind} class="size-4" />
				<Label for="kind-chrome">Chrome</Label>
			</div>
			<div class="flex items-center gap-2">
				<input id="kind-firefox" type="radio" value="firefox" bind:group={kind} class="size-4" />
				<Label for="kind-firefox">Firefox</Label>
			</div>
		</div>
		<p class="text-sm text-muted-foreground">
			{#if kind === 'firefox'}
				Start Firefox with <code>firefox --marionette</code> so scrollforme can attach to it.
			{:else}
				Open <code>chrome://inspect/#remote-debugging</code> once and allow remote debugging. Chrome asks
				you to approve when scrollforme connects.
			{/if}
		</p>
	</Card.Content>
</Card.Root>
