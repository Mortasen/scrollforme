<script lang="ts">
	import { page } from '$app/state';
</script>

<main class="mx-auto max-w-2xl space-y-2 p-6">
	<h1 class="text-xl font-semibold">Something went wrong</h1>
	<p class="text-muted-foreground">{page.error?.message}</p>
	<p class="text-sm text-muted-foreground">
		Is the API running? Start it with <code>uv run scrollforme serve</code>.
	</p>
</main>
