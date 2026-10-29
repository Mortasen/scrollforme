import { getJson, type RawConfig, type RunState, type RunSummary } from '#lib/api/client.js';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const [runs, current, config] = await Promise.all([
		getJson<RunSummary[]>('/api/runs', fetch),
		getJson<RunState>('/api/runs/current', fetch),
		getJson<{ exists: boolean; config: RawConfig }>('/api/config', fetch)
	]);
	return { runs, current, sources: config.config.sources };
};
