/**
 * Interpret a Claude Code or Codex hook payload as file edits.
 *
 * Claude edits files through Edit, MultiEdit, Write and NotebookEdit with `tool_input.file_path`.
 * Codex edits through `apply_patch`, whose patch text arrives in `tool_input.command`. Both run
 * shell commands as `Bash` with `tool_input.command`, which can only be inspected heuristically.
 */
import path from 'node:path';
import { readOrNull } from './standard-lib.ts';


/** The fields of a hook payload this module reads. */
export type HookPayload = { tool_name?: string; tool_input?: any; cwd?: string };

/** A planned edit: `after` is the simulated content, null for a deletion, undefined if unknown. */
export type PlannedEdit = { file: string; after: string | null | undefined };

type Replacement = { old_string?: string; new_string?: string; replace_all?: boolean };
type PatchSection = { kind: string; file: string; lines: string[] };

const CLAUDE_FILE_TOOLS = new Set(['Edit', 'MultiEdit', 'Write', 'NotebookEdit']);
const PATCH_HEADER = /^\*\*\* (Add|Update|Delete) File: (.+)$/;
const PATCH_MOVE = /^\*\*\* Move to: (.+)$/;


/** Return the planned edits in a payload, with absolute paths. */
export function plannedEdits(payload: HookPayload): PlannedEdit[] {
	const tool = payload.tool_name ?? '';
	const input = payload.tool_input ?? {};
	if (CLAUDE_FILE_TOOLS.has(tool)) return [claudeEdit(tool, input, payload.cwd ?? '.')];
	if (tool === 'apply_patch') return patchEdits(String(input.command ?? ''), payload.cwd ?? '.');
	return [];
}


/** Return the absolute paths a payload edits through a file tool. */
export function editedFiles(payload: HookPayload): string[] {
	return plannedEdits(payload).map((edit) => edit.file);
}


function claudeEdit(tool: string, input: any, cwd: string): PlannedEdit {
	const file = path.resolve(cwd, String(input.file_path ?? input.notebook_path ?? ''));
	if (tool === 'Write') return { file, after: String(input.content ?? '') };
	if (tool === 'Edit') return { file, after: applyReplacements(file, [input]) };
	if (tool === 'MultiEdit') return { file, after: applyReplacements(file, input.edits ?? []) };
	return { file, after: undefined };
}


function applyReplacements(file: string, replacements: Replacement[]): string | undefined {
	let text = readOrNull(file) ?? '';
	for (const { old_string: oldText = '', new_string: newText = '', replace_all: all } of replacements) {
		if (!text.includes(oldText)) return undefined;
		text = all ? text.split(oldText).join(newText) : text.replace(oldText, () => newText);
	}
	return text;
}


/** Split an apply_patch text into per-file edits and simulate each one. */
export function patchEdits(patch: string, cwd = '.'): PlannedEdit[] {
	const sections: PatchSection[] = [];
	let current: PatchSection | null = null;
	for (const line of patch.split('\n')) {
		const header = PATCH_HEADER.exec(line);
		const move = PATCH_MOVE.exec(line);
		if (header) sections.push(current = { kind: header[1]!, file: path.resolve(cwd, header[2]!.trim()), lines: [] });
		else if (move && current) sections.push({ kind: 'Move', file: path.resolve(cwd, move[1]!.trim()), lines: current.lines });
		else if (current && line !== '*** End Patch') current.lines.push(line);
	}
	return sections.map(simulatePatch);
}


function simulatePatch({ kind, file, lines }: PatchSection): PlannedEdit {
	if (kind === 'Delete') return { file, after: null };
	if (kind === 'Add') return { file, after: addedText(lines) };
	if (kind === 'Move') return { file, after: undefined };
	return { file, after: applyHunks(readOrNull(file) ?? '', lines) };
}


function addedText(lines: string[]): string {
	return lines.filter((line) => line.startsWith('+')).map((line) => line.slice(1)).join('\n') + '\n';
}


/** Apply the `@@` hunks of an Update File section; undefined when a hunk does not match. */
export function applyHunks(text: string, lines: string[]): string | undefined {
	let result = text;
	let from = 0;
	for (const hunk of splitHunks(lines)) {
		const before = hunk.filter((l) => !l.startsWith('+')).map((l) => l.slice(1)).join('\n');
		const after = hunk.filter((l) => !l.startsWith('-')).map((l) => l.slice(1)).join('\n');
		const at = result.indexOf(before, from);
		if (at < 0) return undefined;
		result = result.slice(0, at) + after + result.slice(at + before.length);
		from = at + after.length;
	}
	return result;
}


function splitHunks(lines: string[]): string[][] {
	const hunks: string[][] = [[]];
	for (const line of lines) {
		if (line.startsWith('@@')) hunks.push([]);
		else if (/^[ +-]/.test(line)) hunks.at(-1)!.push(line);
		else if (line === '') hunks.at(-1)!.push(' ');
	}
	return hunks.filter((hunk) => hunk.length);
}


/** Return the shell command of a Bash payload, or null for any other tool. */
export function shellCommand(payload: HookPayload): string | null {
	return payload.tool_name === 'Bash' ? String(payload.tool_input?.command ?? '') : null;
}
