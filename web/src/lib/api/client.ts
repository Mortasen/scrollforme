/** Typed calls to the local scrollforme API (`scrollforme serve`). */

export type Source = { module: string; description: string };

export type AgentConfig = {
	model: string;
	effort: string;
	max_turns: number;
	max_budget_usd: number;
};

export type BrowserConfig = { kind: 'chrome' | 'firefox'; marionette_port: number };

export type RawConfig = { sources: Source[]; agent: AgentConfig; browser: BrowserConfig } & Record<
	string,
	unknown
>;

export type Check = { name: string; ok: boolean; detail: string };

export type RunSummary = { id: string; generated_at: string; sites: string[]; failed: string[] };

export type RunState = {
	status: 'idle' | 'running' | 'finished' | 'failed';
	started_at: string;
	total: number;
	index: number;
	current_module: string;
	run_id: string;
	error: string;
};

type Fetch = typeof fetch;

/** GET a JSON resource, throwing the API's error detail on failure. */
export async function getJson<T>(path: string, fetcher: Fetch = fetch): Promise<T> {
	return parse<T>(await fetcher(path));
}

/** Send JSON with `method`; every state-changing call sends a JSON body, as the API requires. */
export async function sendJson<T>(method: string, path: string, body: unknown = {}): Promise<T> {
	const headers = { 'Content-Type': 'application/json' };
	return parse<T>(await fetch(path, { method, headers, body: JSON.stringify(body) }));
}

/** The URL of a saved run's digest page. */
export function digestUrl(runId: string): string {
	return `/api/runs/${encodeURIComponent(runId)}/digest`;
}

async function parse<T>(response: Response): Promise<T> {
	const body = await response.json().catch(() => ({}));
	if (!response.ok) throw new Error(body.detail ?? `request failed (${response.status})`);
	return body as T;
}
