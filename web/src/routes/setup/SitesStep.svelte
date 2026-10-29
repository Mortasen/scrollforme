<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Label } from '#lib/components/ui/label/index.js';
	import { Checkbox } from '#lib/components/ui/checkbox/index.js';
	import { Textarea } from '#lib/components/ui/textarea/index.js';
	import type { Source } from '#lib/api/client.js';

	let { modules, sources = $bindable() }: { modules: string[]; sources: Source[] } = $props();

	function sourceFor(module: string): Source | undefined {
		return sources.find((source) => source.module === module);
	}

	function toggle(module: string, checked: boolean) {
		sources = checked
			? [...sources, { module, description: '' }]
			: sources.filter((source) => source.module !== module);
	}
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>2. Choose your sites</Card.Title>
		<Card.Description>
			Say in your own words what you use each site for. The agent takes only that, then stops.
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-5">
		{#if modules.length === 0}
			<p class="text-sm text-muted-foreground">No modules found in the modules folder.</p>
		{/if}
		{#each modules as module (module)}
			{@const source = sourceFor(module)}
			<div class="space-y-2">
				<div class="flex items-center gap-2">
					<Checkbox
						id="site-{module}"
						checked={source !== undefined}
						onCheckedChange={(checked) => toggle(module, checked === true)}
					/>
					<Label for="site-{module}">{module}</Label>
				</div>
				{#if source}
					<Label for="description-{module}" class="sr-only">What you use {module} for</Label>
					<Textarea
						id="description-{module}"
						bind:value={source.description}
						placeholder="e.g. I follow r/LocalLLaMA for new open models; skip memes and drama."
					/>
				{/if}
			</div>
		{/each}
	</Card.Content>
</Card.Root>
