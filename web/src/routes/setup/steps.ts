/** The wizard's screens, one question each, in order. */

import type { RawConfig } from '#lib/api/client.js';

export type Step =
	| { kind: 'browser' }
	| { kind: 'checks' }
	| { kind: 'sites' }
	| { kind: 'describe'; module: string }
	| { kind: 'limits' };

/** Every screen for `config`: one "what do you use it for" screen per chosen site. */
export function stepsFor(config: RawConfig): Step[] {
	const describe = config.sources.map((source): Step => ({
		kind: 'describe',
		module: source.module
	}));
	return [
		{ kind: 'browser' },
		{ kind: 'checks' },
		{ kind: 'sites' },
		...describe,
		{ kind: 'limits' }
	];
}

/** Whether the user has answered `step` well enough to go on. */
export function isAnswered(step: Step, config: RawConfig): boolean {
	if (step.kind === 'sites') return config.sources.length > 0;
	if (step.kind === 'limits') return config.agent.max_budget_usd > 0;
	if (step.kind !== 'describe') return true;
	const source = config.sources.find((candidate) => candidate.module === step.module);
	return Boolean(source?.description.trim());
}
