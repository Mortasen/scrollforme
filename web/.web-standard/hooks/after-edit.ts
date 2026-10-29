#!/usr/bin/env node
/**
 * PostToolUse check for Claude Code and Codex.
 *
 * After any edit or shell command it reports drift from what `web-standard sync` delivered, and
 * after a file edit it lints the edited files with the project's ESLint. Exit code 2 with the
 * findings on stderr returns them to the agent in both tools, so it fixes them while it is still
 * working on the file.
 */
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { editedFiles, type HookPayload } from './edits.ts';
import { OWNER_ROUTE, driftFindings, logHookRun, readManifest, type Manifest } from './standard-lib.ts';


const ROOT = path.resolve(import.meta.dirname, '..', '..');
const LINTED = /\.(svelte|ts|js|mjs|cjs)$/;


main();


function main() {
	const manifest = readManifest(ROOT);
	if (!manifest) return;
	const payload = JSON.parse(readFileSync(0, 'utf8'));
	const report = [...driftReport(manifest), ...lintReport(lintTargets(payload))];
	logHookRun('after-edit', payload, report.length ? report.join('\n') : 'clean');
	if (!report.length) return;
	process.stderr.write(report.join('\n') + '\n');
	process.exit(2);
}


function driftReport(manifest: Manifest): string[] {
	const findings = driftFindings(ROOT, manifest);
	if (!findings.length) return [];
	return [
		'web-standard drift: the project no longer matches what the standard delivered.',
		...findings.map((finding) => `  - ${finding}`),
		'Restore it with `git checkout -- <file>` or `web-standard sync`. If the standard itself',
		`should change, tell the user. ${OWNER_ROUTE}`,
	];
}


function lintTargets(payload: HookPayload): string[] {
	return editedFiles(payload)
		.filter((file) => LINTED.test(file) && existsSync(file))
		.filter((file) => !path.relative(ROOT, file).startsWith('..'));
}


function lintReport(files: string[]): string[] {
	if (!files.length) return [];
	const eslint = path.join(ROOT, 'node_modules', '.bin', 'eslint');
	if (!existsSync(eslint)) return ['web-standard lint: ESLint is not installed; run `pnpm install`, then continue.'];
	const run = spawnSync(eslint, ['--no-warn-ignored', ...files], { cwd: ROOT, encoding: 'utf8' });
	if (run.status === 0) return [];
	const output = (run.stdout || run.stderr || run.error?.message || '').trim();
	return ['web-standard lint: fix these before continuing; the rules cannot be disabled here.', output];
}
