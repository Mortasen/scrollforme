import { redirect } from '@sveltejs/kit';
import { getJson, type RawConfig } from '#lib/api/client.js';
import type { PageLoad } from './$types';

/** Send first-time users to setup and everyone else to the dashboard. */
export const load: PageLoad = async ({ fetch }) => {
	const { exists } = await getJson<{ exists: boolean; config: RawConfig }>('/api/config', fetch);
	redirect(307, exists ? '/dashboard' : '/setup');
};
