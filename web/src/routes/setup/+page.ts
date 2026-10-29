import { getJson, type Check, type RawConfig } from '#lib/api/client.js';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const [setup, config] = await Promise.all([
		getJson<{ checks: Check[]; modules: string[] }>('/api/setup', fetch),
		getJson<{ exists: boolean; config: RawConfig }>('/api/config', fetch)
	]);
	return { ...setup, ...config };
};
