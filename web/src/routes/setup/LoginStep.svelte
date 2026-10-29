<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import { sendJson } from '#lib/api/client.js';

	let { saved }: { saved: boolean } = $props();
	let opening = $state(false);
	let opened = $state(false);
	let error = $state('');

	async function openBrowser() {
		opening = true;
		error = '';
		try {
			await sendJson('POST', '/api/login');
			opened = true;
		} catch (problem) {
			error = (problem as Error).message;
		} finally {
			opening = false;
		}
	}
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>4. Log in once</Card.Title>
		<Card.Description>
			Opens Chrome on scrollforme's own profile at each site. Log in, then close the window. The
			logins stay for every later run.
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-2">
		<Button variant="outline" disabled={!saved || opening} onclick={openBrowser}>
			{opening ? 'Opening…' : 'Open the login browser'}
		</Button>
		{#if !saved}
			<p class="text-xs text-muted-foreground">Save your sites first.</p>
		{/if}
		{#if opened}
			<p class="text-sm">Chrome is open. Close it when you have logged in everywhere.</p>
		{/if}
		{#if error}
			<p class="text-sm text-destructive" role="alert">{error}</p>
		{/if}
	</Card.Content>
</Card.Root>
