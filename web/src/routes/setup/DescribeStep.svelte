<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Label } from '#lib/components/ui/label/index.js';
	import { Textarea } from '#lib/components/ui/textarea/index.js';
	import type { Source } from '#lib/api/client.js';

	let { source = $bindable() }: { source: Source } = $props();
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>What do you use {source.module} for?</Card.Title>
		<Card.Description>
			In your own words. scrollforme collects only that, then stops.
		</Card.Description>
	</Card.Header>
	<Card.Content>
		<Label for="description" class="sr-only">What you use {source.module} for</Label>
		<Textarea
			id="description"
			rows={4}
			bind:value={source.description}
			placeholder="e.g. I follow r/LocalLLaMA for new open models; skip memes and drama."
		/>
	</Card.Content>
</Card.Root>
