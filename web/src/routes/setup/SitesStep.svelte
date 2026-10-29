<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Label } from '#lib/components/ui/label/index.js';
	import { Checkbox } from '#lib/components/ui/checkbox/index.js';
	import type { Source } from '#lib/api/client.js';

	let { modules, sources = $bindable() }: { modules: string[]; sources: Source[] } = $props();

	function isChosen(module: string): boolean {
		return sources.some((source) => source.module === module);
	}

	function toggle(module: string, checked: boolean) {
		sources = checked
			? [...sources, { module, description: '' }]
			: sources.filter((source) => source.module !== module);
	}
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Which sites do you check?</Card.Title>
		<Card.Description>Pick every site you want scrollforme to read for you.</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-3">
		{#if modules.length === 0}
			<p class="text-sm text-muted-foreground">No modules found in the modules folder.</p>
		{/if}
		{#each modules as module (module)}
			<div class="flex items-center gap-2">
				<Checkbox
					id="site-{module}"
					checked={isChosen(module)}
					onCheckedChange={(checked) => toggle(module, checked === true)}
				/>
				<Label for="site-{module}">{module}</Label>
			</div>
		{/each}
	</Card.Content>
</Card.Root>
