/**
 * Project-side core of web-standard, delivered into `.web-standard/hooks/`.
 *
 * Dependency-free on purpose: a project's hooks must run without the web-standard checkout, so
 * this uses only Node built-ins and Node 22's TypeScript type stripping. The CLI imports the same
 * module, so drift is defined once for `check` and for the hooks.
 */
import { createHash } from 'node:crypto';
import { appendFileSync, existsSync, lstatSync, readFileSync, readlinkSync } from 'node:fs';
import path from 'node:path';


export const STANDARD_DIR = '.web-standard';
export const MANIFEST_PATH = `${STANDARD_DIR}/manifest.json`;
export const HOOK_PATH_MARKER = `/${STANDARD_DIR}/hooks/`;
export const SECTION_BEGIN = '<!-- web-standard:begin';
export const SECTION_END = '<!-- web-standard:end -->';
export const CLAUDE_IMPORT_LINE = '@AGENTS.md';
export const GITIGNORE_LINE = `${STANDARD_DIR}/screenshots/`;
export const PRETTIERIGNORE_LINE = `${STANDARD_DIR}/`;
export const OWNER_ROUTE = 'Standard-owned files are changed only in /f/Tools/web-standard and '
	+ 'delivered with `web-standard sync`; project lint rules belong in eslint.project.js.';

/** Files holding a part web-standard manages while the project owns the rest. */
export const MANAGED_FILES = ['AGENTS.md', 'CLAUDE.md', '.claude/settings.json', 'package.json', '.gitignore', '.prettierignore'];
export const LINT_COMMAND = 'eslint .';
export const SCREENSHOT_SCRIPT = `node ${STANDARD_DIR}/tools/screenshot.ts`;

/** What `sync` recorded: owned file hashes, links, required dev dependencies, managed-part hashes. */
export type Manifest = {
	standard: { version: string; commit: string; dirty: boolean };
	files: Record<string, string>;
	links: Record<string, string>;
	devDependencies: string[];
	managed: Record<string, string>;
};

type HookGroup = { matcher?: string; hooks?: { command?: string }[] };
type Json = any;


/**
 * Append a hook's payload and outcome to the file named by WEB_STANDARD_HOOK_LOG, when set. Used to
 * prove in live sessions that a hook fired and to capture real payloads as test fixtures.
 */
export function logHookRun(hook: string, payload: unknown, outcome: string): void {
	const file = process.env.WEB_STANDARD_HOOK_LOG;
	if (file) appendFileSync(file, JSON.stringify({ hook, outcome, payload }) + '\n');
}


/** Return the SHA-256 hex digest of a string. */
export function sha256(text: string): string {
	return createHash('sha256').update(text).digest('hex');
}


/** Read the manifest `sync` recorded, or null when the project has none. */
export function readManifest(root: string): Manifest | null {
	const file = path.join(root, MANIFEST_PATH);
	return existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : null;
}


/** Report whether a project-relative path is owned whole by the standard. */
export function isOwnedPath(manifest: Manifest, relPath: string): boolean {
	const rel = toPosix(relPath);
	if (rel === STANDARD_DIR || rel.startsWith(`${STANDARD_DIR}/`)) return true;
	return Object.hasOwn(manifest.files, rel) || Object.hasOwn(manifest.links, rel)
		|| Object.keys(manifest.links).some((link) => rel.startsWith(`${link}/`));
}


/**
 * Return the fingerprint of the part of a managed file the standard owns, or null if absent.
 * The manifest supplies the dev dependency names the standard requires.
 */
export function managedPart(relPath: string, content: string | null, manifest: Pick<Manifest, 'devDependencies'>): string | null {
	if (content === null) return null;
	const extract = MANAGED_EXTRACTORS[toPosix(relPath)];
	return extract ? extract(content, manifest.devDependencies) : null;
}


const MANAGED_EXTRACTORS: Record<string, (text: string, devDependencies: string[]) => string | null> = {
	'AGENTS.md': agentsSection,
	'CLAUDE.md': (text) => hasLine(text, CLAUDE_IMPORT_LINE) ? CLAUDE_IMPORT_LINE : null,
	'.claude/settings.json': (text) => stableJson(standardHookGroups(parseJson(text))),
	'package.json': (text, devDependencies) => stableJson(managedPackageFields(parseJson(text), devDependencies)),
	'.gitignore': (text) => hasLine(text, GITIGNORE_LINE) ? GITIGNORE_LINE : null,
	'.prettierignore': (text) => hasLine(text, PRETTIERIGNORE_LINE) ? PRETTIERIGNORE_LINE : null,
};


/** Return the marked standard section of AGENTS.md, markers included, or null. */
export function agentsSection(text: string): string | null {
	const begin = text.indexOf(SECTION_BEGIN);
	const end = text.indexOf(SECTION_END);
	if (begin < 0 || end < begin) return null;
	return text.slice(begin, end + SECTION_END.length);
}


/** Return the hook matcher groups whose commands run the standard's hook scripts, per event. */
export function standardHookGroups(settings: Json): Record<string, HookGroup[]> {
	const hooks: Record<string, HookGroup[]> = settings?.hooks ?? {};
	const result: Record<string, HookGroup[]> = {};
	for (const [event, groups] of Object.entries(hooks)) {
		const ours = (groups ?? []).filter(isStandardHookGroup);
		if (ours.length) result[event] = ours;
	}
	return result;
}


/** Report whether a hook matcher group runs one of the standard's scripts. */
export function isStandardHookGroup(group: unknown): boolean {
	const hooks = (group as HookGroup | null)?.hooks ?? [];
	return hooks.some((hook) => String(hook.command ?? '').includes(HOOK_PATH_MARKER));
}


/**
 * Settings files in which an agent's hooks can be switched off wholesale, and the test for each.
 * Claude Code honours `disableAllHooks` in project and local settings (measured in the 2.1.291
 * binary); Codex honours `[features] hooks = false` (or the deprecated `codex_hooks`) in a
 * project `.codex/config.toml` (Codex hooks documentation). Turning hooks off would silence the
 * guard and the after-edit check without touching anything else the standard fingerprints.
 */
export const HOOK_OFF_SWITCHES: Record<string, (text: string) => boolean> = {
	'.claude/settings.json': (text) => parseJson(text)?.disableAllHooks === true,
	'.claude/settings.local.json': (text) => parseJson(text)?.disableAllHooks === true,
	'.codex/config.toml': codexHooksDisabled,
};


function codexHooksDisabled(toml: string): boolean {
	if (/^\s*features\.(codex_)?hooks\s*=\s*false\b/m.test(toml)) return true;
	const table = /^\s*\[features\]\s*$([\s\S]*?)(?=^\s*\[|(?![\s\S]))/m.exec(toml);
	return table !== null && /^\s*(codex_)?hooks\s*=\s*false\b/m.test(table[1] ?? '');
}


/** Return a finding for each project settings file that switches the agents' hooks off. */
export function hookOffSwitchFindings(root: string): string[] {
	return Object.entries(HOOK_OFF_SWITCHES).flatMap(([rel, disables]) => {
		const text = readOrNull(path.join(root, rel));
		return text !== null && disables(text) ? [`${rel}: switches the agent hooks off`] : [];
	});
}


/**
 * Return the package.json fields the standard manages: whether `lint` runs ESLint over the whole
 * project, the `screenshot` script, and which required dev dependencies are present. Versions and
 * the rest of `lint` (such as a Prettier check) are the project's.
 */
export function managedPackageFields(pkg: Json, requiredDevDependencies: string[]) {
	const steps = String(pkg?.scripts?.lint ?? '').split(/&&|;/).map((step) => step.trim());
	const lintRunsEslint = steps.includes(LINT_COMMAND);
	const scripts = { lintRunsEslint, screenshot: pkg?.scripts?.screenshot ?? null };
	const names = Object.keys(pkg?.devDependencies ?? {});
	return { scripts, devDependencies: requiredDevDependencies.filter((name) => names.includes(name)).sort() };
}


/**
 * List every way the project differs from what `sync` delivered: owned files edited, links
 * changed, or a managed part altered. Returns human-readable findings.
 *
 * Read-only mode is reported only on request (`check` asks; the after-edit hook does not). Git
 * does not record it, so every clone and every `git checkout` restores owned files writable; as a
 * blocking finding it would stop agents on every edit in a fresh clone. It is a signal that
 * `sync` reasserts, not a guard.
 */
export function driftFindings(root: string, manifest: Manifest | null = readManifest(root), options: { modes?: boolean } = {}): string[] {
	if (!manifest) return [`${MANIFEST_PATH} is missing; run web-standard sync`];
	return [
		...ownedFileFindings(root, manifest, options.modes ?? false),
		...linkFindings(root, manifest),
		...managedFindings(root, manifest),
		...hookOffSwitchFindings(root),
	];
}


function ownedFileFindings(root: string, manifest: Manifest, modes: boolean): string[] {
	const findings: string[] = [];
	for (const [rel, hash] of Object.entries(manifest.files)) {
		const content = readOrNull(path.join(root, rel));
		if (content === null) findings.push(`${rel}: owned file is missing`);
		else if (sha256(content) !== hash) findings.push(`${rel}: owned file was edited`);
		else if (modes && isWritable(path.join(root, rel))) findings.push(`${rel}: owned file lost its read-only mode; run web-standard sync`);
	}
	return findings;
}


function linkFindings(root: string, manifest: Manifest): string[] {
	const findings: string[] = [];
	for (const [rel, target] of Object.entries(manifest.links)) {
		if (readLinkOrNull(path.join(root, rel)) !== target) findings.push(`${rel}: link should point to ${target}`);
	}
	return findings;
}


function managedFindings(root: string, manifest: Manifest): string[] {
	const findings: string[] = [];
	for (const [rel, hash] of Object.entries(manifest.managed)) {
		const part = managedPart(rel, readOrNull(path.join(root, rel)), manifest);
		if (part === null) findings.push(`${rel}: the standard's part is missing`);
		else if (sha256(part) !== hash) findings.push(`${rel}: the standard's part was edited`);
	}
	return findings;
}


/** Return a file's text, or null when it does not exist. */
export function readOrNull(file: string): string | null {
	return existsSync(file) ? readFileSync(file, 'utf8') : null;
}


function readLinkOrNull(file: string): string | null {
	try {
		return lstatSync(file).isSymbolicLink() ? readlinkSync(file) : null;
	} catch {
		return null;
	}
}


function isWritable(file: string): boolean {
	return (lstatSync(file).mode & 0o222) !== 0;
}


/** Serialise JSON with sorted object keys, so fingerprints ignore key order. */
export function stableJson(value: unknown): string {
	return JSON.stringify(value, (_key, item) => isPlainObject(item) ? sortKeys(item) : item);
}


function sortKeys(object: Record<string, unknown>): Record<string, unknown> {
	return Object.fromEntries(Object.entries(object).sort(([a], [b]) => a.localeCompare(b)));
}


function isPlainObject(value: unknown): value is Record<string, unknown> {
	return value !== null && typeof value === 'object' && !Array.isArray(value);
}


function parseJson(text: string): Json {
	try {
		return JSON.parse(text);
	} catch {
		return null;
	}
}


function hasLine(text: string, line: string): boolean {
	return text.split(/\r?\n/).some((candidate) => candidate.trim() === line);
}


/** Convert a path to forward slashes for comparison with manifest keys. */
export function toPosix(relPath: string): string {
	return relPath.split(path.sep).join('/');
}
