/**
 * Decision rules of the PreToolUse edit guard, kept apart from its entry script so tests can call
 * them without stdin. See guard.mjs.
 */
import path from 'node:path';
import { plannedEdits, shellCommand, type HookPayload, type PlannedEdit } from './edits.ts';
import { HOOK_OFF_SWITCHES, MANAGED_FILES, isOwnedPath, managedPart, readOrNull, toPosix, type Manifest } from './standard-lib.ts';


const OWNED_SHELL_TOKENS = ['eslint.config.js', '.web-standard', '.codex/hooks.json', 'skills/frontend'];
const SHELL_WRITE = /(^|[^<&0-9])>{1,2}|\btee\b|\b(sed|perl)\b[^|;&]*\s-i|\b(rm|mv|cp|chmod|chown|ln|truncate|dd|install|unlink|rsync)\b/;
const SHELL_ALLOWED = /^\s*(git|web-standard|\S*\/bin\/web-standard)\b/;
const SHELL_CHAINING = /[;&|`<>]|\$\(/;


/** Return why the payload must be denied, or null to allow it. */
export function denialReason(payload: HookPayload, manifest: Manifest, root: string): string | null {
	const command = shellCommand(payload);
	if (command !== null) return shellDenial(command);
	for (const edit of plannedEdits(payload)) {
		const reason = editDenial(edit, manifest, root);
		if (reason) return reason;
	}
	return null;
}


function editDenial({ file, after }: PlannedEdit, manifest: Manifest, root: string): string | null {
	const rel = toPosix(path.relative(root, file));
	if (rel.startsWith('..')) return null;
	if (isOwnedPath(manifest, rel)) return `${rel} is owned by the web standard and cannot be edited here.`;
	const disables = HOOK_OFF_SWITCHES[rel];
	if (disables && typeof after === 'string' && disables(after)) return `this edit to ${rel} would switch the agent hooks off.`;
	if (!MANAGED_FILES.includes(rel) || after === undefined) return null;
	const before = managedPart(rel, readOrNull(file), manifest);
	const changed = before !== managedPart(rel, after, manifest);
	return changed ? `this edit changes the web standard's part of ${rel}.` : null;
}


function shellDenial(command: string): string | null {
	const exempt = SHELL_ALLOWED.test(command) && !SHELL_CHAINING.test(command);
	if (exempt || !SHELL_WRITE.test(command)) return null;
	const token = OWNED_SHELL_TOKENS.find((owned) => command.includes(owned));
	return token ? `this shell command appears to modify ${token}, which the web standard owns.` : null;
}
