#!/usr/bin/env node
/**
 * PreToolUse edit guard for Claude Code and Codex.
 *
 * Denies an edit to a standard-owned file or to the standard's part of a managed file, even when
 * the user asked for it: those change only in web-standard. Exit code 2 with the reason on stderr
 * denies the call in both agents. Anything it cannot interpret is allowed; the after-edit hook
 * still catches the resulting drift.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { denialReason } from './guard-rules.ts';
import { OWNER_ROUTE, logHookRun, readManifest } from './standard-lib.ts';


const ROOT = path.resolve(import.meta.dirname, '..', '..');


const manifest = readManifest(ROOT);
const payload = JSON.parse(readFileSync(0, 'utf8'));
const reason = manifest && denialReason(payload, manifest, ROOT);
logHookRun('guard', payload, reason || 'allow');
if (reason) {
	process.stderr.write(`web-standard guard: ${reason}\n${OWNER_ROUTE}\n`);
	process.exit(2);
}
